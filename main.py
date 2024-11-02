import random
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
from db import DB
from llm import llm
import json

PORT = 60000
app = Flask(__name__)
CORS(app)
db = DB("game_database.db")

# Handles drawing =======================================
socketio = SocketIO(app, cors_allowed_origins="*")
@socketio.on('draw')
def handle_draw(data):
    emit('draw', data, broadcast=True)

# Handles drawing =======================================



@app.route('/createGame', methods=["POST"])
def createRoom():
    username = request.headers.get("username")

    if not username:
        return {"error": "Username is required"}, 400

    # Insert a new game
    gameQuery = "INSERT INTO Game (theme, game_status, start_time) VALUES (?, ?, ?)"
    startTime = datetime.now().isoformat()
    gameID = db.insertAndFetch(gameQuery, ("Default", "drawing", startTime))
    
    if gameID is None:
        return {"error": "Failed to create game"}, 500  # Handle case where ID is None

    # Insert the new player into the Player table
    playerQuery = "INSERT INTO Player (player_name, role, game_id) VALUES (?, ?, ?)"
    role = "drawer"  # Assign a default role, modify as needed based on your logic
    playerID = db.insertAndFetch(playerQuery, (username, role, gameID))

    if playerID is None:
        return {"error": "Failed to create player"}, 500  # Handle player insertion failure

    # # Link player to game id using prompt table
    # promptQuery = "INSERT INTO Prompt (player_id, game_id, main_prompt, side_prompt) VALUES (?, ?, ?, ?)"
    # mainPrompt = "Main prompt text"
    # sidePrompt = "Secondary prompt"

    # # Insert the prompt for the new game
    # if db.insert(promptQuery, (playerID, gameID, mainPrompt, sidePrompt)) is None:
    #     return {"error": "Failed to create prompt"}, 500  # Handle prompt insertion failure

    return {"gameID": gameID, "playerID": playerID}, 200



@app.route("/joinGame", methods=["POST"])
def joinGame():
    username = request.headers.get("username")
    gameID = request.json.get("gameID")

    if not username:
        return {"error": "Username is required"}, 400
    
    if not gameID:
        return {"error": "Game ID is required"}, 400
    
    # Check if the game exists
    gameExistsQuery = "SELECT COUNT(*) FROM Game WHERE game_id = ?"
    gameExists = db.select(gameExistsQuery, (gameID,))

    if gameExists is None or gameExists[0][0] == 0:
        return {"error": "Game does not exist"}, 404
    # Check if the game exists and how many players are in it
    playerCountQuery = "SELECT COUNT(*) FROM Player WHERE game_id = ?"
    currentPlayerCount = db.select(playerCountQuery, (gameID,))

    if currentPlayerCount is None or currentPlayerCount[0][0] >= 5:
        return {"error": "Game is full or does not exist"}, 400

    # Insert the new player into the Player table
    playerQuery = "INSERT INTO Player (player_name, role, game_id) VALUES (?, ?, ?)"

    if currentPlayerCount[0][0] + 1 == 3:
        assignRandomGuesser(gameID)

    playerID = db.insertAndFetch(playerQuery, (username, "drawer", gameID))

    if playerID is None:
        return {"error": "Failed to create player"}, 500  # Handle player insertion failure
    socketio.emit('player_update', {'username': username, 'gameID': gameID}, room=gameID)
    return {"gameID": gameID, "playerID": playerID, "username": username}, 200

def assignRandomGuesser(gameID):
    playersQuery = "SELECT player_id FROM Player WHERE game_id = ?"
    players = db.select(playersQuery, (gameID,))
    guesser_id = random.choice(players)[0]
    updateRoleQuery = "UPDATE Player SET role = 'guesser' WHERE player_id = ?"
    db.update(updateRoleQuery, (guesser_id,))

def get_roles(gameID):
    rolesQuery = "SELECT player_name, role FROM Player WHERE game_id = ?"
    roles = db.select(rolesQuery, (gameID,))
    return [{"player_name": player[0], "role": player[1]} for player in roles]

def emit_roles(gameID):
    rolesQuery = "SELECT player_id, role FROM Player WHERE game_id = ?"
    roles = db.select(rolesQuery, (gameID,))

    for player_id, role in roles:
        socketio.emit('role_assigned', {'role': role}, room=f'player_{player_id}')  # Use a unique room for each player

@socketio.on('join')
def handle_join(data):
    gameID = data['gameID']
    playerID = data['playerID']
    join_room(gameID)  # Join the game room
    join_room(f'player_{playerID}') 

@app.route("/readyup", methods=["POST"])
def readyUp():
    playerID = request.json.get("playerID")
    gameID = request.json.get("gameID")

    if not playerID or not gameID:
        return {"error": "playerID and gameID are required"}, 400

    # Update the ready status of the player
    readyQuery = "UPDATE Player SET is_ready = ? WHERE player_id = ? and game_id = ?"
    if db.update(readyQuery, (True, playerID, gameID)) == 0:
        return {"error": "Failed to update ready status or player not found"}, 404

    # Check if all players are ready
    checkReadyQuery = "SELECT COUNT(*) FROM PLAYER WHERE game_id = ? and is_ready = FALSE"
    unreadyCount = db.select(checkReadyQuery, (gameID,))
    
    if unreadyCount and unreadyCount[0][0] == 0:
        # Retrieve the guesser for the game
        guesserQuery = "SELECT player_id FROM Player WHERE game_id = ? AND role = 'guesser'"
        guesser = db.select(guesserQuery, (gameID,))
        guesser_id = guesser[0][0] if guesser else None

        # Start the game and notify players
        socketio.emit('game_start', {'guesser_id': guesser_id}, room=gameID)
        assign_prompts(gameID)
        return {"message": "All players are ready. Game started!", "guesser_id": guesser_id}, 200

    return {"message": "Player is ready. Waiting for others."}, 200



@socketio.on('join')
def handle_join(data):
    gameID = data['gameID']
    join_room(gameID)  # Join the room corresponding to the gameID
    emit('player_update', {'players': get_players(gameID)}, room=gameID)  # Send current players

def get_players(gameID):
    playersQuery = "SELECT player_name FROM Player WHERE game_id = ?"
    players = db.select(playersQuery, (gameID,))
    return [player[0] for player in players]


@socketio.on("ready")
def handleReady(data):
    gameID = data['gameID']
    if gameID in ready_players:
        ready_players[gameID].append(request.sid)

# Handle theme votes
THEMES = ["random", "halloween", "christmas", "easter"]
gameVotes = {}
@socketio.on('vote')
def handle_vote(data):
    game_id = data["gameID"]
    player_id = data["playerID"]
    theme = data["theme"]

    if game_id not in gameVotes:
        socketio.emit("error", {"message": "Voting not started."})
        return

    gameVotes[game_id]["votes"][player_id] = theme
    total_votes = len(gameVotes[game_id]["votes"])

    # Check if all players have voted
    if total_votes >= gameVotes[game_id]["total_players"]:
        # Calculate winning theme (here, a simple count of votes)
        theme_counts = {}
        for vote in gameVotes[game_id]["votes"].values():
            theme_counts[vote] = theme_counts.get(vote, 0) + 1
        winning_theme = max(theme_counts, key=theme_counts.get)
        socketio.emit("vote_result", {"theme": winning_theme}, room=game_id)
        print("votes", winning_theme)
        del gameVotes[game_id]  # Reset votes
    emit("vote_update", {"votes": total_votes}, room=game_id)

@app.route("/assign_prompts", methods=["POST"])
def assign_prompts():
    data = request.json
    gameID = data.get("gameID")
    player_count = data.get("player_count")

    if not gameID or not player_count:
        return {"error": "gameID and player_count are required"}, 400

    llm_instance = llm(count=player_count)
    main_prompt, secondary_prompts = llm_instance.assign_prompts(player_count)

    # Save prompts to the database or send to clients
    prompts_query = "INSERT INTO Prompt (game_id, main_prompt, secondary_prompts) VALUES (?, ?, ?)"
    db.insert(prompts_query, (gameID, main_prompt, json.dumps(secondary_prompts)))

    # Notify players about their assigned prompts
    socketio.emit('prompts_assigned', {'main_prompt': main_prompt, 'secondary_prompts': secondary_prompts}, room=gameID)

    return {"main_prompt": main_prompt, "secondary_prompts": secondary_prompts}, 200


@app.route("/check_guess", methods=["POST"])
def check_guess():
    data = request.json
    player_id = data.get("player_id")  # Get the player ID from the request
    guess = data.get("guess")
    game_id = data.get("game_id")

    if not player_id or not guess or not game_id:
        return {"error": "player_id, guess, and game_id are required"}, 400

    # Fetch the correct answer for the current game
    correct_answer_query = "SELECT main_prompt FROM Prompt WHERE game_id = ?"
    correct_answer_row = db.select(correct_answer_query, (game_id,))
    
    if not correct_answer_row:
        return {"error": "No prompts found for this game"}, 404
    
    correct_answer = correct_answer_row[0]['main_prompt']

    # Check if the guess is correct
    is_correct = guess.lower() == correct_answer.lower()

    # Save the guess to the database
    insert_guess_query = "INSERT INTO Guesses (game_id, player_id, guess, is_correct) VALUES (?, ?, ?, ?)"
    db.insert(insert_guess_query, (game_id, player_id, guess, is_correct))

    return {"is_correct": is_correct}, 200

if __name__ == "__main__":
    socketio.run(app,port=PORT)
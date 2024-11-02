from flask import Flask, request
from flask_socketio import SocketIO, emit
from datetime import datetime
from db import DB

PORT = 60000
app = Flask(__name__)
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
    role = "drawer"  # Assign a default role; modify as needed based on your logic
    playerID = db.insertAndFetch(playerQuery, (username, role, gameID))

    if playerID is None:
        return {"error": "Failed to create player"}, 500  # Handle player insertion failure

    return {"gameID": gameID, "playerID": playerID, "username": username}, 200

@app.route("/readyup", methods=["POST"])
def readyUp():
    playerID = request.json.get("playerID")
    gameID = request.json.get("gameID")

    if not playerID or not gameID:
        return {"error": "playerID and gameID are required"}, 400

    readyQuery = "UPDATE Player SET is_ready = ? WHERE player_id = ? and game_id = ?"
    if db.update(readyQuery, (True, playerID, gameID)) == 0:
        return {"error": "Failed to update ready status or player not found"}, 404
    
    checkReadyQuery = "SELECT COUNT(*) FROM PLAYER WHERE game_id = ? and is_ready = FALSE"
    unreadyCount = db.select(checkReadyQuery, (gameID,))
    
    if unreadyCount and unreadyCount[0][0] == 0:
        print("Start game!")
        return {"message": "All players are ready. Game started!"}, 200
    return {"message": "Player is ready. Waiting for others."}, 200




if __name__ == "__main__":
    socketio.run(app,port=PORT)
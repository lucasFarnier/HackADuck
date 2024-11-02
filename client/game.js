async function createGame() {
    const username = document.getElementById("Username").value;
    try {
        const response = await fetch("http://localhost:60000/createGame", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "username": username
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Failed to create game");
        }

        const data = await response.json();
        console.log("Game created successfully:", data);
        localStorage.setItem("playerID", data.playerID)
        window.location.href = `lobby.html?gameID=${data.gameID}`

        // use the player id in the lobby.html
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error("Error creating game:", error.message);
        
    }
}

async function handleJoinGame() {
    const username = document.getElementById("Username").value;
    const gameID = document.getElementById("Code").value;

    if (!username || !gameID) {
        alert("Please enter both a username and a game code.");
        return;
    }

    await joinGame(username, gameID);
}

async function joinGame(username, gameID) {
    try {
        const response = await fetch("http://localhost:60000/joinGame", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "username": username
            },
            body: JSON.stringify({ gameID }) // Pass gameID in the body
        });
        console.log(response)
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Failed to join game");
        }

        const data = await response.json();
        console.log("Joined game successfully:", data);
        
        // Store playerID and redirect to lobby page
        localStorage.setItem("playerID", data.playerID);
        window.location.href = `lobby.html?gameID=${data.gameID}`;

    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error("Error joining game:", error.message);
    }
}

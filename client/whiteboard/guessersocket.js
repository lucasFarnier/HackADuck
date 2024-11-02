const canvas = document.getElementById('whiteboard');
        const ctx = canvas.getContext('2d');
        let drawing = false;
        let drawingAllowed = false; // Variable to track if drawing is allowed
        const socket = io('http://127.0.0.1:60000');

        // Set up line properties
        ctx.strokeStyle = "#000000";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";

        // Timer setup
        const updateTimer = () => {
            const now = new Date();
            const unixTimestamp = Math.floor(now.getTime() / 1000);
            let futureTimestamp = localStorage.getItem('futureTimestamp');

            // If it doesn't exist, create it and store it in localStorage
            if (!futureTimestamp) {
                futureTimestamp = unixTimestamp + 60;
                localStorage.setItem('futureTimestamp', futureTimestamp);
            }

            // Calculate remaining time
            const timer = futureTimestamp - unixTimestamp;
            document.getElementById('timer').textContent = `Timer: ${timer}`;

            // Check if the timer has ended
            if (unixTimestamp >= futureTimestamp) {
                alert("End of timer");
                localStorage.removeItem('futureTimestamp');
                drawingAllowed = false; // Disable drawing
                clearInterval(timerInterval); // Stop the timer
            }
        };

        // Update the timer every second
        const timerInterval = setInterval(updateTimer, 1000);

        
        // Listen for color changes from other users
        socket.on('changeColor', (color) => {
            ctx.strokeStyle = color; // Set color based on the received color
            });
            
        // Listen for drawing events from other users
        socket.on('draw', (data) => {
            ctx.strokeStyle = data.color; // Set color based on data received
            ctx.beginPath(); // Start a new path
            ctx.moveTo(data.startX, data.startY); // Move to the start position
            ctx.lineTo(data.endX, data.endY); // Draw line to the end position
            ctx.stroke();
        });
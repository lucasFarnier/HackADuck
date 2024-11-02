const canvas = document.getElementById('whiteboard');
        const ctx = canvas.getContext('2d');
        let drawing = false;
        let drawingAllowed = true; // Variable to track if drawing is allowed
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

        // Start drawing
        canvas.addEventListener("mousedown", (e) => {
            if (!drawingAllowed) return; // Prevent drawing if not allowed
            drawing = true;
            ctx.beginPath();
            ctx.moveTo(e.offsetX, e.offsetY);
            socket.emit('draw', { x: e.offsetX, y: e.offsetY, isDown: true });
        });

        // Draw lines
        canvas.addEventListener("mousemove", (e) => {
            if (!drawing || !drawingAllowed) return; // Prevent drawing if not allowed
            ctx.lineTo(e.offsetX, e.offsetY);
            ctx.stroke();
            socket.emit('draw', { x: e.offsetX, y: e.offsetY, isDown: true });
        });

        // Stop drawing
        canvas.addEventListener("mouseup", () => {
            drawing = false;
            ctx.closePath();
        });

        // Stop drawing if cursor leaves canvas
        canvas.addEventListener("mouseleave", () => {
            drawing = false;
        });

        // Listen for drawing events from other users
        socket.on('draw', (data) => {
            ctx.lineTo(data.x, data.y);
            ctx.stroke();
        });
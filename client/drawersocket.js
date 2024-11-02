const canvas = document.getElementById('whiteboard');
        const ctx = canvas.getContext('2d');
        let drawing = false;
        let drawingAllowed = true; // Variable to track if drawing is allowed
        const socket = io('http://127.0.0.1:60000');


        let button1 = document.getElementById("colour1");
        let button2 = document.getElementById("colour2");
        let colour1 = `#${Math.floor(Math.random()*16777215).toString(16)}`
        let colour2 = `#${Math.floor(Math.random()*16777215).toString(16)}`
        button1.style.backgroundColor = colour1;
        button2.style.backgroundColor = colour2;

        button1.addEventListener("click", function() {
            ctx.strokeStyle = colour1;
            button1.style.borderColor = "white";
            button2.style.borderColor = "black";
            button1.style.width = "74%"
            button2.style.width = "24%"
        });
        button2.addEventListener("click", function() {
            ctx.strokeStyle = colour2;
            button2.style.borderColor = "white";
            button1.style.borderColor = "black";
            button2.style.width = "74%"
            button1.style.width = "24%"
        });


        // Set up line properties
        ctx.strokeStyle = colour1;
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
        
        let lastX, lastY; // Store last position

       // Start drawing
        canvas.addEventListener("mousedown", (e) => {
            if (!drawingAllowed) return; // Prevent drawing if not allowed
            drawing = true;
            lastX = e.offsetX;
            lastY = e.offsetY;
            // Send the starting point with color
            socket.emit('draw', { x: e.offsetX, y: e.offsetY, isDown: true, color: ctx.strokeStyle });
        });

        // Draw lines
        canvas.addEventListener("mousemove", (e) => {
            if (!drawing || !drawingAllowed) return; // Prevent drawing if not allowed
            
            // Draw locally with the current color
            ctx.strokeStyle = ctx.strokeStyle;  // Use the current selected color
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(e.offsetX, e.offsetY);
            ctx.stroke();
            ctx.closePath();
            
            // Send the line segment data along with the color
            socket.emit('draw', { x: e.offsetX, y: e.offsetY, isDown: false, color: ctx.strokeStyle });

            // Update last position
            lastX = e.offsetX;
            lastY = e.offsetY;
        });

        // Stop drawing
        canvas.addEventListener("mouseup", () => {
            drawing = false;
            // Emit an event with the end point and color to finish the line
            socket.emit('draw', { x: lastX, y: lastY, isDown: false, color: ctx.strokeStyle, endLine: true });
        });

        // Listen for drawing events from other users
        socket.on('draw', (data) => {
            // Set the color for each line segment individually
            let currentColor = ctx.strokeStyle;
            ctx.strokeStyle = data.color;
            if (data.isDown) {
                // Begin a new path with the specified color
                ctx.beginPath();
                ctx.moveTo(data.x, data.y);
            } else {
                // Continue the path with the specified color
                ctx.lineTo(data.x, data.y);
                ctx.stroke();
            }
            if (data.endLine) {
                // Close the path when the drawing stops
                ctx.closePath();
            }
            ctx.strokeStyle = currentColor;
        });


        
        // Listen for color changes from other users
        socket.on('changeColor', (color) => {
        ctx.strokeStyle = color; // Set color based on the received color
        });
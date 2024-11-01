const canvas = document.getElementById('whiteboard');
        const ctx = canvas.getContext('2d');
        let drawing = false;
        const socket = io();

        // Set up line properties
        ctx.strokeStyle = "#000000";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";

        // Start drawing
        canvas.addEventListener("mousedown", (e) => {
            drawing = true;
            ctx.beginPath();
            ctx.moveTo(e.offsetX, e.offsetY);
            socket.emit('draw', { x: e.offsetX, y: e.offsetY, isDown: true });
        });

        // Draw lines
        canvas.addEventListener("mousemove", (e) => {
            if (!drawing) return;
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
            if (data.isDown) {
                ctx.lineTo(data.x, data.y);
                ctx.stroke();
            } else {
                ctx.closePath();
            }
        });
const canvas = document.getElementById('whiteboard');
  const ctx = canvas.getContext('2d');
  const socket = io('http://localhost:60000'); // Connect to the Flask-SocketIO server
  let drawing = false;

  // Set up line properties
  ctx.strokeStyle = "#000000";
  ctx.lineWidth = 2;
  ctx.lineCap = "round";

  // Start drawing
  canvas.addEventListener("mousedown", (e) => {
    drawing = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
  });

  // Draw lines and send data to server
  canvas.addEventListener("mousemove", (e) => {
    if (!drawing) return;
    const x = e.offsetX;
    const y = e.offsetY;
    ctx.lineTo(x, y);
    ctx.stroke();

    // Send drawing data to server
    socket.emit('draw', { x, y });
  });

  // Stop drawing
  canvas.addEventListener("mouseup", () => {
    drawing = false;
  });

  // Stop drawing if cursor leaves canvas
  canvas.addEventListener("mouseleave", () => {
    drawing = false;
  });

  // Listen for draw events from server and draw on canvas
  socket.on('draw', (data) => {
    ctx.lineTo(data.x, data.y);
    ctx.stroke();
  });
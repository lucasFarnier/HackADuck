const canvas = document.getElementById('whiteboard');
  const ctx = canvas.getContext('2d');
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

  // Draw lines
  canvas.addEventListener("mousemove", (e) => {
    if (!drawing) return;
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
  });

  // Stop drawing
  canvas.addEventListener("mouseup", () => {
    drawing = false;
  });

  // Stop drawing if cursor leaves canvas
  canvas.addEventListener("mouseleave", () => {
    drawing = false;
  });
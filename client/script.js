document.getElementById("openPopup").onclick = function() {
    document.getElementById("popup").style.display = "flex"; // Show the popup
};

document.querySelector(".close").onclick = function() {
    document.getElementById("popup").style.display = "none"; // Hide the popup
};

// Close the popup if the user clicks anywhere outside of the popup content
window.onclick = function(event) {
    if (event.target == document.getElementById("popup")) {
        document.getElementById("popup").style.display = "none";
    }
};
const shiftModal = document.getElementById("shiftModal");
const milkModal = document.getElementById("milkModal");
const closeButtons = document.querySelectorAll(".close");

closeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        btn.closest(".modal").style.display = "none";
    });
});


window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal")) {
        e.target.style.display = "none";
    }
});


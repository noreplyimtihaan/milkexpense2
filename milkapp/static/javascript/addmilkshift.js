const addShiftBtn = document.getElementById("addShiftBtn");
const shiftModal = document.getElementById("shiftModal");
const select = document.getElementById("shiftSelect");
import reloadCalendar from './calendar.js'


if (addShiftBtn && shiftModal) {
    addShiftBtn.addEventListener('click', () => {
        shiftModal.style.display = "flex";
    })

}

if (select) {
    const selected = select.querySelector(".selected-option");
    const options = select.querySelectorAll(".option");
    const hiddenInput = document.getElementById("selectedShift");

    if (selected && hiddenInput) {
        selected.onclick = () => {
            select.classList.toggle("active");
        };

        options.forEach(option => {

            option.onclick = () => {

                selected.textContent = option.textContent;

                hiddenInput.value = option.dataset.value;

                select.classList.remove("active");
                reloadCalendar();
            };

        });

        document.addEventListener("click", function (e) {

            if (!select.contains(e.target)) {
                select.classList.remove("active");
            }

        });
    }
}


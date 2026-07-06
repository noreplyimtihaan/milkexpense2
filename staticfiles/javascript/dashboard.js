const filterForm = document.getElementById("dashboardFilterForm");
const shiftSelect = document.getElementById("dashboardShiftSelect");
const selectedOption = shiftSelect?.querySelector(".selected-option");
const options = shiftSelect?.querySelectorAll(".option");
const hiddenInput = document.getElementById("dashboardShiftBy");
const prevMonthBtn = document.querySelector('.dashboard-month-nav button[value="prev_month"]');
const nextMonthBtn = document.querySelector('.dashboard-month-nav button[value="next_month"]');

if (filterForm && shiftSelect && selectedOption && hiddenInput && !shiftSelect.classList.contains("disabled")) {
    selectedOption.addEventListener("click", () => {
        shiftSelect.classList.toggle("active");
    });

    selectedOption.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            shiftSelect.classList.toggle("active");
        }
    });

    options.forEach(option => {
        option.addEventListener("click", () => {
            const nextValue = option.dataset.value || "";

            selectedOption.textContent = option.textContent.trim();
            hiddenInput.value = nextValue;
            shiftSelect.classList.remove("active");

            filterForm.submit();
        });
    });

    document.addEventListener("click", (event) => {
        if (!shiftSelect.contains(event.target)) {
            shiftSelect.classList.remove("active");
        }
    });
}

document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;

    const target = event.target;
    if (target instanceof Element && target.closest("input, textarea, select, .custom-select, [contenteditable='true']")) return;

    const monthButton = event.key === "ArrowLeft" ? prevMonthBtn : nextMonthBtn;
    if (!monthButton || monthButton.disabled) return;

    event.preventDefault();
    monthButton.click();
});

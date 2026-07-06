const calendar = document.getElementById("calendar");
const monthYear = document.getElementById("monthYear");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const selectedShift = document.getElementById("selectedShift");
const shiftSelect = document.getElementById("shiftSelect");

const modal = document.getElementById("milkModal");


import getCookie from "./getCookie.js";

const today = new Date();

let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

const maxDate = new Date(today.getFullYear(), today.getMonth(), 1);
const minDate = new Date(today.getFullYear(), today.getMonth() - 5, 1);

const state = {};
let clickTimer;
function renderCalendar(month, year) {
    if (!calendar || !monthYear || !prevBtn || !nextBtn) return;

    calendar.innerHTML = "";
    const firstDay = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();

    monthYear.textContent = new Date(year, month).toLocaleString("default", {
        month: "long",
        year: "numeric",
    });

    for (let i = 0; i < firstDay; i++) {
        const box = document.createElement("div");
        box.className = "empty";
        calendar.appendChild(box);
    }

    for (let d = 1; d <= totalDays; d++) {
  
        const box = document.createElement("div");
        box.className = "day";

        const dayNumber = document.createElement("span");
        dayNumber.className = "day-number";
        dayNumber.textContent = d;

        const editIcon = document.createElement("span");
        editIcon.className = "edit-icon";
        editIcon.innerHTML = "✏️";

        box.appendChild(dayNumber);
        box.appendChild(editIcon);
        const date = new Date(year, month, d);
        const key = `${year}-${month}-${d}`;

        if (date.toDateString() == today.toDateString())
            box.classList.add("today");

        if (date > today) {
            box.classList.add("disabled");
        } else {
            box.classList.remove("green", "red");

            if (state[key] == "Present")
                box.classList.add("green");

            if (state[key] == "Absent")
                box.classList.add("red");

            box.addEventListener("click", async () => {
               
                    if (state[key] == null || state[key] === "")
                        state[key] = "Present";
                    else if (state[key] === "Present")
                        state[key] = "Absent";
                    else
                        delete state[key];

                    try {
                        const response = await fetch("/update_state/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": getCookie("csrftoken"),
                            },
                            body: JSON.stringify({
                                shift_id: selectedShift.value,
                                date: `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`,
                                status: state[key] || null,
                            }),
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP Error: ${response.status}`);
                        }

                        renderCalendar(currentMonth, currentYear);
                    } catch (error) {
                        await loadCalendar(currentMonth, currentYear);
                    }
                });
            


            editIcon.addEventListener("click", function () {
                

                const date = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`
                fetch(`/get_milk_shifts/${selectedShift.value}/?date=${date}`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.success) {

                            return;
                        }
                        milkLiter.value = data.default_liter;
                        milkPrice.value = data.default_price;
                        // Entry date
                        entryDate.value = date
                        shiftID.value = selectedShift.value

                        modal.style.display = "flex";
                    }).catch(error => {

                    });



            });
        }

        calendar.appendChild(box);
    }

    prevBtn.disabled = (new Date(year, month, 1) <= minDate);
    nextBtn.disabled = (new Date(year, month, 1) >= maxDate);
}

async function loadCalendar(month, year) {
    if (!shiftSelect || !selectedShift || !selectedShift.value) return;

    currentMonth = month;
    currentYear = year;

    try {
        const response = await fetch(`/get_month_states/?shift_id=${selectedShift.value}&year=${year}&month=${month + 1}`);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        Object.keys(state).forEach(k => delete state[k]);
        Object.assign(state, data.states);
        renderCalendar(month, year);
    } catch (error) {
    }
}

export default function reloadCalendar() {
    return loadCalendar(currentMonth, currentYear);
}

if (calendar && monthYear && prevBtn && nextBtn && selectedShift) {
    prevBtn.onclick = function () {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        loadCalendar(currentMonth, currentYear);
    };

    nextBtn.onclick = function () {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        loadCalendar(currentMonth, currentYear);
    };

    loadCalendar(currentMonth, currentYear);
}

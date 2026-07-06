const profileBtn = document.getElementById("profileBtn");
const profileMenu = document.getElementById("profileMenu");

if(profileBtn && profileMenu){

    profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        profileMenu.classList.toggle("show");
    });
}
if(profileBtn && profileMenu){

    document.addEventListener("click", (e) => {
        if (!profileMenu.contains(e.target) && !profileBtn.contains(e.target)) {
            profileMenu.classList.remove("show");
        }
    });
}

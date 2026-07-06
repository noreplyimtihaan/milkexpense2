// message close
const closeMessage=document.getElementById("closeMessage")

if(closeMessage){
    closeMessage.addEventListener('click',()=>{
        document.querySelector(".message-modal").style.display = "none";
    })

}




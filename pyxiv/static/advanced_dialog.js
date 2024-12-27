const button = document.getElementById("advanced-open")
const dialog = document.getElementById("advanced")
const close = document.getElementById("advanced-close")

close.addEventListener("click", ()=>{
    dialog.removeAttribute("data-visible")
})

button.addEventListener("click", ()=>{
    dialog.setAttribute("data-visible", "")
})
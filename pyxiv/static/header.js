const upButton = document.querySelector("#user-profile")
const acMenu = document.querySelector("#account-menu")

upButton.addEventListener("click", ()=>{
  if (!acMenu.getAttribute("data-open")) {
    acMenu.setAttribute("data-open", "1");
  } else {
    acMenu.removeAttribute("data-open")
  }
})

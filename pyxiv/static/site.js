document.addEventListener("DOMContentLoaded", ()=>{
	menuButton = document.querySelector("header #menu")
	menuUiBackdrop = document.querySelector("#main-menu.backdrop")
	menuUi = document.querySelector("#main-menu .main")
	closeButton = document.querySelector("#main-menu .main #close")

	menuButton.addEventListener("click", ()=>{
		menuUiBackdrop.setAttribute("data-visible", "")
		setTimeout(()=>{menuUi.setAttribute("data-visible", "")})
	})

	closeButton.addEventListener("click", ()=>{
		menuUiBackdrop.removeAttribute("data-visible")
		menuUi.removeAttribute("data-visible")
	})
})


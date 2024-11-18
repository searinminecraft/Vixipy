document.addEventListener("DOMContentLoaded", ()=>{
	menuButton = document.querySelector("header #menu")
	menuUiBackdrop = document.querySelector("#main-menu.backdrop")
	menuUi = document.querySelector("#main-menu .main")
	closeButton = document.querySelector("#main-menu .main #close")

	if (document.documentElement.getAttribute("data-logged-in") != null) {
		accountMenuButton = document.querySelector("header #user-profile")
		accountMenuUiBackdrop = document.querySelector("#account-menu.backdrop")
		accountMenuUi = document.querySelector("#account-menu .main")
		accountMenuCloseButton = document.querySelector("#account-menu .main #close")

		accountMenuCloseButton.addEventListener("click", ()=>{
			accountMenuUiBackdrop.removeAttribute("data-visible")
			accountMenuUi.removeAttribute("data-visible")
		})

		accountMenuButton.addEventListener("click", ()=>{
			accountMenuUiBackdrop.setAttribute("data-visible", "")
			setTimeout(()=>{accountMenuUi.setAttribute("data-visible", "")})
		})
	}

	menuButton.addEventListener("click", ()=>{
		menuUiBackdrop.setAttribute("data-visible", "")
		setTimeout(()=>{menuUi.setAttribute("data-visible", "")})
	})

	closeButton.addEventListener("click", ()=>{
		menuUiBackdrop.removeAttribute("data-visible")
		menuUi.removeAttribute("data-visible")
	})
})


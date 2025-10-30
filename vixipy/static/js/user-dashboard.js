document.getElementById("logout-btn").addEventListener("click", (e) => {
    document.querySelector("div[popover]#logout").togglePopover()
    e.preventDefault()
})
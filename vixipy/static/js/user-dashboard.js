document.getElementById("logout").addEventListener("click", (e)=>{
    var c = confirm(document.getElementById("i18n-logout-string").value)
    if (!c) {
        e.preventDefault()
    }
})
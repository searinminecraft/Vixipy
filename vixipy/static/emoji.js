document.querySelectorAll("#emojis button").forEach(element => {
    element.addEventListener("click", ()=>{
        document.querySelector("textarea").value += `(${element.value})`
    })
});
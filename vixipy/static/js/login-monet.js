const xhr = new XMLHttpRequest()
xhr.open("GET", `/api/illust/${document.getElementById("illust_id").value}/material-you`, true)
xhr.send()
xhr.onreadystatechange = ()=>{
    if (xhr.readyState === 4 && xhr.status === 200) {
        const st = document.createElement("style")
        st.textContent = xhr.responseText
        document.body.appendChild(st)
    }
}
const getScheme = (type, id) => {
    const xhr = new XMLHttpRequest()
    xhr.open("GET", `/api/${type}/${id}/material-you`, true)
    xhr.send()
    xhr.onreadystatechange = ()=>{
        if (xhr.readyState === 4 && xhr.status === 200) {
            const st = document.createElement("style")
            st.textContent = xhr.responseText
            document.body.appendChild(st)
    	}
    }

}

const getSchemeFromArtwork = (id) => {getScheme("illust", id)}
const getSchemeFromUser = (id) => {getScheme("user", id)}

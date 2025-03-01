var cachedMessages = []
const chat = document.querySelector(".chat")
const threadId = chat.getAttribute("data-thread-id")
currentUser = parseInt(document.getElementById("current-user").value)

function updateMessages() {
    data = fetch(`/api/messages/${threadId}/contents`)
        .then((resp)=>{
            resp.json().then((json)=>{
                for (const c in json.contents) {
                    cur = json.contents[c]
                    if (!cachedMessages.includes(cur.id)) {
                        m = document.createElement("div")
                        if (cur.userid == currentUser) {
                            m.setAttribute("class", "message self")
                        } else {
                            m.setAttribute("class", "message")
                        }
                        img = document.createElement("img")
                        img.setAttribute("class", "profile")
                        img.setAttribute("src", cur.icon)

                        let cont

                        if (cur.type == "image") {
                            cont = document.createElement("a")
                            cont.setAttribute("href", cur.image)
                            cimg = document.createElement("img")
                            cimg.setAttribute("class", "content-img")
                            cimg.setAttribute("src", cur.thumbnail)
                            cont.appendChild(cimg)
                        } else {
                            cont = document.createElement("div")
                            cont.setAttribute("class", "content")
                            cont.innerHTML = cur.text
                        }

                        m.append(img, cont)
                        chat.prepend(m)

                        cachedMessages = cachedMessages.concat(cur.id)
                    }
                }
            })
        }).catch(null)
}

existing = chat.querySelectorAll(".message")
for (const e of existing) {
    cachedMessages = cachedMessages.concat(parseInt(e.getAttribute("data-content-id")))
}
setInterval(updateMessages, 10000)

document.addEventListener("DOMContentLoaded", ()=>{
    const fpWrapper = document.querySelector(".file-preview-wrapper")
    const filePreview = document.getElementById("img-preview")
    const filenameLabel = document.getElementById("filename")
    const removeAttachment = document.getElementById("remove-attachment")
    const picker = document.getElementById("uploader")

    picker.addEventListener("change", ()=>{
        file = picker.files[0]
        filenameLabel.innerHTML = file.name
        blob = URL.createObjectURL(file)
        filePreview.src = blob
        fpWrapper.style.display = "block"
    })

    removeAttachment.addEventListener("click", ()=>{
        picker.value = ""
        fpWrapper.style.display = "none"
    })
})
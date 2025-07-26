// this code is bad and doesnt work properly. dont bother.

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const artwork_container = document.querySelector(".artwork-container")
var last_id = document.getElementById("last_id").value
var progress = false

window.addEventListener("scroll", () => {
    if ((window.innerHeight + window.pageYOffset) >= document.body.offsetHeight - 2) {
        if (progress) return

        progress = true
        fetch(`/api/illust/new?last_id=${last_id}&r18=${Boolean(urlParams.get('r18') == 'true')}`).then((res) => {
            res.json().then((data) => {
                if (data.error) {
                    progress = false
                } else {

                    for (const x of data.body.illusts) {
                        const artwork_entry = document.createElement("div")
                        artwork_entry.className = "artwork-entry"

                        const img_container = document.createElement("div")
                        img_container.className = "img-container"

                        const meta = document.createElement("div")
                        meta.className = "meta"

                        const meta_left = document.createElement("div")
                        const meta_right = document.createElement("div")

                        if (x.ai) {
                            let tag = document.createElement("div")
                            tag.className = "tag ai"
                            tag.innerHTML = "AI"
                            meta_left.appendChild(tag)
                        }

                        if (x.r18) {
                            let tag = document.createElement("div")
                            tag.className = "tag r18"
                            tag.innerHTML = "R-18"
                            meta_left.appendChild(tag)
                        }

                        if (x.page_count > 1) {
                            let tag = document.createElement("div")
                            tag.className = "tag"
                            tag.innerHTML = x.page_count
                            meta_right.appendChild(tag)
                        }

                        meta.append(meta_left, meta_right)
                        img_container.appendChild(meta)

                        const img_link = document.createElement("a")
                        img_link.href = `/artworks/${x.id}`

                        const img = document.createElement("img")
                        img.src = x.thumb
                        img.alt = x.alt
                        img.loading = "lazy"

                        img_link.appendChild(img)
                        img_container.appendChild(img_link)
                        artwork_entry.appendChild(img_container)


                        const title = document.createElement("a")
                        title.className = "title"
                        title.title = x.title
                        title.innerHTML = x.title
                        title.href = `/artworks/${x.id}`

                        artwork_entry.appendChild(title)

                        const author_link = document.createElement("a")
                        author_link.className = "author"
                        author_link.href = `/users/${x.user_id}`
                        
                        const author_img = document.createElement("img")
                        author_img.src = x.profile_image
                        author_img.loading = "lazy"
                        author_link.appendChild(author_img)
                        author_link.innerHTML += ` ${x.user_name}`
                        
                        artwork_entry.appendChild(author_link)

                        artwork_container.appendChild(artwork_entry)
                    }
                    progress = false
                    last_id = data.body.last_id
                }
            })
        }).catch(() => { })
    }
})

var timeout
const suggest_list = $(".suggestions")

function get_suggestions() {
    const query = $(".searchbox input").val()
    $.get(
        `/api/search/autocomplete?keyword=${encodeURIComponent(query)}`,
        (r, s, xhr) => {
            if (xhr.status != 200) {
                suggest_list.html("")
                suggest_list.removeAttr("data-open")
                return
            }
            if (xhr.responseJSON.body.length == 0) {
                suggest_list.html("")
                suggest_list.removeAttr("data-open")
                return
            }

            suggest_list.html("")
            suggest_list.attr("data-open", "")

            for (const res of xhr.responseJSON.body) {
                li = document.createElement("li")
                link = document.createElement("a")
                link.href = `/tags/${res.name}`
                span = document.createElement("span")
                span.innerHTML = res.name
                link.append(span)
                if (res.sub) {
                    sub = document.createElement("small")
                    sub.innerHTML = res.sub
                    link.append(sub)
                }
                li.append(link)
                suggest_list.append(li)
            }
        }
    )
}

$(".searchbox input").on("input", (e) => {
    if (e.target.value == "") {
        $(".suggestions").removeAttr("data-open")
        return
    }

    if (!timeout) {
        timeout = setTimeout(get_suggestions, 200)
    } else {
        clearTimeout(timeout)
        timeout = setTimeout(get_suggestions, 200)
    }
})
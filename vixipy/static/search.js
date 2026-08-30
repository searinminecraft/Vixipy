(function(){
"use strict";

let timeout
const suggest_list = $(".suggestions")

$(".searchbox input").focus()

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
                let li = document.createElement("li")
                let link = document.createElement("a")
                link.href = `/tags/${res.name}`
                let span = document.createElement("span")
                span.textContent = res.name
                link.append(span)
                if (res.sub) {
                    let sub = document.createElement("small")
                    sub.textContent = res.sub
                    link.append(sub)
                }

                li.append(link)
                suggest_list.append(li)
		htmx.process(link)
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
})()

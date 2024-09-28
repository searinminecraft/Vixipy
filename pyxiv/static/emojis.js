if (document.documentElement.getAttribute("data-logged-in") != null) {
	emojiCloseButton = document.getElementById("emoji-close")
	emojiOpenButton = document.getElementById("open-emoji")
	emojis = document.querySelectorAll(".dialog .emojis .emoji-button")
	emojiDialog = document.getElementById("emoji-dialog")
	commentBox = document.getElementById("comment-box")

	emojiOpenButton.addEventListener("click", ()=>{emojiDialog.setAttribute("data-visible", "")})
	emojiCloseButton.addEventListener("click", ()=>{emojiDialog.removeAttribute("data-visible")})
	for (const emoji of emojis) {
		emoji.addEventListener("click", ()=>{
			commentBox.value += ` (${emoji.id})`
		})
	}

}

if (document.documentElement.getAttribute("data-logged-in") != null) {
	const deleteButtons = document.querySelectorAll("#delete-comment")
	for (const l of deleteButtons) {
		l.addEventListener("click", (e)=>{
			if (!confirm("Are you sure you want to delete this comment and all of its replies?")) {
				e.preventDefault()
			}
		})
	}
}

const pfp_picker = document.getElementById("pfp-picker")
const pfp_preview = document.getElementById("pfp")
const banner_picker = document.getElementById("banner-picker")
const banner_preview = document.getElementById("banner")

const update_preview = (t)=>{

  let maxSize
  let prev
  let picker
  let files
  
  if (t === 0) {
    maxSize = 1024*1024*5
    prev = pfp_preview
    picker = pfp_picker
    files = picker.files
  } else if (t === 1) {
    maxSize = 1024*1024*8
    prev = banner_preview
    picker = banner_picker
    files = picker.files
  }

  if (files.length >= 1) {
    if (!["image/png", "image/jpeg", "image/gif"].includes(files[0].type)) {
      alert(strs.invalidType)
      picker.value = ""
      return
    }
    if (files[0].size >= maxSize) {
      alert(`${strs.tooLarge} (${files[0].size / (1024*1024)} > ${maxSize / (1024*1024)})`)
      picker.value = ""
      return
    }

    url = URL.createObjectURL(files[0])
    prev.src = url
  }
}

pfp_picker.addEventListener("change", ()=>{update_preview(0)})
banner_picker.addEventListener("change", ()=>{update_preview(1)})

// =========================================

const modified_inputs = new Set;
const defaultValue = "defaultValue";
// store default values
addEventListener("beforeinput", (evt) => {
    const target = evt.target;
    if (!(defaultValue in target || defaultValue in target.dataset)) {
        target.dataset[defaultValue] = ("" + (target.value || target.textContent)).trim();
    }
});
// detect input modifications
addEventListener("input", (evt) => {
    const target = evt.target;
    let original;
    if (defaultValue in target) {
        original = target[defaultValue];
    } else {
        original = target.dataset[defaultValue];
    }
    if (original !== ("" + (target.value || target.textContent)).trim()) {
        if (!modified_inputs.has(target)) {
            modified_inputs.add(target);
        }
    } else if (modified_inputs.has(target)) {
        modified_inputs.delete(target);
    }
});
// clear modified inputs upon form submission
addEventListener("submit", (evt) => {
    modified_inputs.clear();
    // to prevent the warning from happening, it is advisable
    // that you clear your form controls back to their default
    // state with evt.target.reset() or form.reset() after submission
});
// warn before closing if any inputs are modified
addEventListener("beforeunload", (evt) => {
    if (modified_inputs.size) {
        const unsaved_changes_warning = "Changes you made may not be saved.";
        evt.returnValue = unsaved_changes_warning;
        return unsaved_changes_warning;
    }
});

$(document).ready(()=>{
    $("input[name=xrestrict]").on("change", (e)=>{
        
        checked = e.target.checked
        if (checked && (e.target.value.startsWith("r18"))) {
            $("#mature").show()
            $("#mature").removeAttr("disabled")
            $("#adult").hide()
            $("#adult").attr("disabled", "")
        } else {
            $("#mature").hide()
            $("#mature").attr("disabled", "")
            $("#adult").show()
            $("#adult").removeAttr("disabled")
        }
    })
})
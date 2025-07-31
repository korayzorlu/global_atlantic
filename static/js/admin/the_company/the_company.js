//Get neccessary fields when add company bank account by Iban or Swift
$(document).ready(function() {
    
    let selected_value=$("#id_translation_type :selected").val();
    get_fields(selected_value);
})

$('#id_translation_type').on('change', function () {
    let selected_value=$("#id_translation_type :selected").val();
    get_fields(selected_value);

})

function get_fields(_selected_value){
    if(_selected_value=="IBAN"){
       document.getElementById("Swift").style.display = "none";
       document.getElementById("IBAN").style.display="block";
       document.getElementById("Currency").style.display="block";
    }
    else if(_selected_value=="SWIFT"){
        console.log("here")
        document.getElementById("Swift").style.display="block";
        document.getElementById("IBAN").style.display="none";
        document.getElementById("Currency").style.display="none";
    }
    else{
        console.log("Invalid value selected")
    }
    console.log(_selected_value)
}
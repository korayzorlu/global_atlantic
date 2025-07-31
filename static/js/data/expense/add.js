function formSubmitMessageExpenseAdd(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
        $("body").busyLoad("show", {
            animation: false,
            spinner: "pulsar",
            maxSize: "150px",
            minSize: "150px",
            text: "Loading ...",
            background: "rgba(69, 83, 89, 0.6)",
            color: "#455359",
            textColor: "#fff"
        });
    
        setTimeout(function() {
            let eSub = "expense-new";

            let navTagSub = $("#navTag-" + eSub);
            let tabPaneSub = $("#tabPane-" + eSub);

            navTagSub.prev().children("a").addClass("active");
            tabPaneSub.prev().addClass("show active");
            
            navTagSub.prev().children("a").children("button").show();
            $("#table-" + ee).DataTable().columns.adjust();
            
            navTagSub.remove();
            tabPaneSub.remove();

            // const backdrop = document.querySelector('#full-backdrop');
            // backdrop.remove();
            // loadingFull.remove();

            
            
            fetch('/data/api/expenses?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                .then((response) => {
                return response.json();
                })
                .then((data) => {
                console.log(data["data"][0]["id"]);
                htmx.ajax("GET", "/data/expense_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                window.history.pushState({}, '', "/data/expense_update/" + data["data"][0]["id"] + "/");
                
                })
            
            setTimeout(function() {
                $("body").busyLoad("hide", {
                animation: "fade"
                });
            }, 1000);
        

        }, 2000);
      
    });
  
  
};




$(document).ready(function () {

    setNavTab();
    setNavTabSub();
    setHTMX();
    formSubmitMessageExpenseAdd();

});
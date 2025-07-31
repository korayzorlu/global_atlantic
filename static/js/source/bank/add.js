function setNavTabBank(){
    let e = elementTag;
    let ef = elementTag;
    let u = pageUrl;
  
    let navTag = $("#navTag-" + e);
    let navTagLink = $("#navTagLink-" + e);
    let tabPane = $("#tabPane-" + e);
    let removeNav = $("#removeNav-" + e);
    let sideBarButton = $(".nav-list li ." + e);
  
    $(".mainNavLink").removeClass("active");
    $(".mainTabPane").removeClass("show active");
  
    $("#tabNav").append(navTag);
    $("#tabCont").append(tabPane);
    navTagLink.addClass("active");
    tabPane.addClass("show active");
  
    $(".mainNavLink:not(.active)").children("button").hide();
  
    sideBarButton.attr("hx-swap", "none");
    $(".home-section").css({"overflow" : "hidden"});
  
    $("#table-" + e).DataTable().columns.adjust();
  
    removeNav.click(function(){
        navTag.prev().children("a").addClass("active");
        tabPane.prev().addClass("show active");
        
        navTag.prev().children("a").children("button").show();
  
        if(navTag.prev().attr("id") == "dashboardNavTag"){
          $(".home-section").css({"overflow" : "hidden"});
        };
        
        navTag.remove();
        tabPane.remove();
  
        sideBarButton.attr("hx-swap", "afterbegin");

        $("#createQuotationButton").removeClass("d-none");
        
    });
  
    navTagLink.on("shown.bs.tab", function(e){
      $(e.target).children("button").show();
      $(e.relatedTarget).children("button").hide();
  
      $("#table-" + ef).DataTable().columns.adjust();
  
      $(".home-section").css({"overflow" : "hidden"});
  
      history.pushState({}, null, u);
    });
  
    navTag.css({"display" : "block"});
  };

function setNavTabSubBank(){
    let eSub = elementTag + "-" + elementTagId;
    let efSub = elementTag;
    let uSub = pageUrl;
  
    let navTagSub = $("#navTag-" + eSub);
    let navTagLinkSub = $("#navTagLink-" + eSub);
    let tabPaneSub = $("#tabPane-" + eSub);
    let removeNavSub = $("#removeNav-" + eSub);
    let sideBarButtonSub = $(".nav-list li ." + eSub);
  
    if($("#navTag-" + eSub + ".hereOn").length > 0){
      $("#navTag-" + eSub + ".hereOn").remove();
      $("#tabPane-" + eSub + ".hereOn").remove();
  
      $("#navTag-" + eSub).addClass("hereOn");
      $("#tabPane-" + eSub).addClass("hereOn");
  
      $(".mainNavLinkSub-" + efSub).removeClass("active");
      $(".mainTabPaneSub-" + efSub).removeClass("show active");
  
      $("#tabNavSub-" + efSub).append(navTagSub);
      $("#tabContSub-" + efSub).append(tabPaneSub);
      navTagLinkSub.addClass("active");
      tabPaneSub.addClass("show active");
  
      $(".mainNavLinkSub:not(.active)").children("button").hide();
      $("#navTag-" + eSub).children("a").children("button").show();
      $("#table-" + eSub).DataTable().columns.adjust();
  
      removeNavSub.click(function(){
        navTagSub.prev().children("a").addClass("active");
        tabPaneSub.prev().addClass("show active");
        navTagSub.prev().children("a").children("button").show();
        $("#table-" + efSub).DataTable().columns.adjust();
        navTagSub.remove();
        tabPaneSub.remove();
        sideBarButtonSub.attr("hx-swap", "afterbegin");
      });
  
      navTagLinkSub.on("shown.bs.tab", function(e){
        $(e.target).children("button").show();
        $(e.relatedTarget).children("button").hide();
        $("#table-" + efSub).DataTable().columns.adjust();
        $("#table-" + eSub).DataTable().columns.adjust();
        history.pushState({}, null, uSub);
      });
  
      navTagSub.css({"display" : "block"});
  
      document.querySelectorAll('.form-outline').forEach((formOutline) => {
        new mdb.Input(formOutline).update();
      });
      
    }else{
      $("#navTag-" + eSub).addClass("hereOn");
      $("#tabPane-" + eSub).addClass("hereOn");
  
      $(".mainNavLinkSub-" + efSub).removeClass("active");
      $(".mainTabPaneSub-" + efSub).removeClass("show active");
  
      $("#tabNavSub-" + efSub).append(navTagSub);
      $("#tabContSub-" + efSub).append(tabPaneSub);
      navTagLinkSub.addClass("active");
      tabPaneSub.addClass("show active");
  
      $(".mainNavLinkSub:not(.active)").children("button").hide();
  
      $("#table-" + eSub).DataTable().columns.adjust();
  
      console.log(removeNavSub);
      removeNavSub.click(function(){
        navTagSub.prev().children("a").addClass("active");
        tabPaneSub.prev().addClass("show active");
        navTagSub.prev().children("a").children("button").show();
        $("#table-" + efSub).DataTable().columns.adjust();
        navTagSub.remove();
        tabPaneSub.remove();
        sideBarButtonSub.attr("hx-swap", "afterbegin");
      });
  
      navTagLinkSub.on("shown.bs.tab", function(e){
          $(e.target).children("button").show();
          $(e.relatedTarget).children("button").hide();
          $("#table-" + efSub).DataTable().columns.adjust();
          $("#table-" + eSub).DataTable().columns.adjust();
          history.pushState({}, null, uSub);
      });
  
      navTagSub.css({"display" : "block"});
  
      document.querySelectorAll('.form-outline').forEach((formOutline) => {
        new mdb.Input(formOutline).update();
      });
      
    };
};

function formSubmitMessageBankAdd(){
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
            let eSub = "bank-new";

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

            
            
            fetch('/source/api/banks?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                .then((response) => {
                return response.json();
                })
                .then((data) => {
                console.log(data["data"][0]["id"]);
                htmx.ajax("GET", "/source/bank_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                window.history.pushState({}, '', "/source/bank_update/" + data["data"][0]["id"] + "/");
                
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
    setNavTabSubBank();
    formSubmitMessageBankAdd();
});
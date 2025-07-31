

function setNavTabProfile(){
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
        
    });
  
    navTagLink.on("shown.bs.tab", function(e){
      $(e.target).children("button").show();
      $(e.relatedTarget).children("button").hide();
  
      $("#table-" + ef).DataTable().columns.adjust();
  
      $(".home-section").css({"overflow" : "hidden"});
  
      history.pushState({}, null, u);
    });
  
    navTag.css({"display" : "block"});

    document.querySelectorAll('.form-outline').forEach((formOutline) => {
        new mdb.Input(formOutline).update();
    });
  };

function setHTMXProfile(){
let ee = elementTag;
let ei = elementTagId;

let tableBox = $(".tableBox-" + ee);
let tableId = "#table-" + ee;
let table = $("#table-" + ee);

//open
htmx.on("htmx:afterSwap", (e) => {
    if(e.detail.target.id == "tabContSub-" + ee){
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
        animation: "fade"
        });
    });
    };
    if (e.detail.target.id == "addUpdateDataDialog-" + ee) {
    console.log(location.href);
    //addUpdateDataModal.show();
    };
});
//submitted
htmx.on("htmx:beforeSwap", (e) => {
    if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
    e.detail.shouldSwap = false;
    };
    if (e.detail.target.id == "addUpdateDataDialog-" + ee && !e.detail.xhr.response) {
    console.log(e.detail.xhr.status);
    //addUpdateDataModal.hide();
    e.detail.shouldSwap = false;
    $(tableId).DataTable().ajax.reload(function(){
        htmx.process(tableId);
    },false);
    };
});
//cancelled
htmx.on("hidden.bs.modal", (e) => {
    if (e.target.id == "addUpdateDataDialog-" + ee) {
    console.log(location.href);
    document.getElementById("addUpdateDataDialog-" + ee).innerHTML = "";
    };
});

};

$(document).ready(function () {
    setNavTabProfile();
    setHTMXProfile();
    
});
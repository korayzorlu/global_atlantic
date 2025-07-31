function setNavTabSubRoom(){
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
  
      // document.querySelectorAll('.form-outline').forEach((formOutline) => {
      //   new mdb.Input(formOutline).update();
      // });
      
    };
};


function setHTMXInquiry(){
    let ee = elementTag;
    let ei = elementTagId;
    let es = elementTagSub + "-" + elementTagId;
  
    let tableBox = $(".tableBox-" + ee);
    let tableId = "#table-" + ee;
    let table = $("#table-" + ee);
  
    //open
    htmx.on("htmx:afterSwap", (e) => {
        if(e.detail.target.id == "tabContSub-" + ee){
            $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("show", {
                animation: false,
                spinner: "pulsar",
                maxSize: "150px",
                minSize: "150px",
                text: "Loading ...",
                background: "rgba(69, 83, 89, 0.6)",
                color: "#455359",
                textColor: "#fff"
            });
            $(tableId).DataTable().ajax.reload(function(){
                htmx.process(tableId);
            },false);
            table.on( 'draw.dt', function () {
                htmx.process(tableId);
                $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
                    animation: "fade"
                });
            });
        };
        if(e.detail.target.id == "addFormBlock-inform-d-justDetail-" + es){
            $("#table-" + es).DataTable().ajax.reload(function(){
                htmx.process("#table-" + es);
            },false);
            
        };
    });
    //submitted
    htmx.on("htmx:beforeSwap", (e) => {
        let addFormBlockSubID = "tabContSub-" + ee;
        if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
                e.detail.shouldSwap = false;
            $(tableId).DataTable().ajax.reload(function(){
                htmx.process(tableId);
            },false);
        };
        if (e.detail.target.id == "addFormBlock-inform-d-justDetail-" + es && !e.detail.xhr.response) {
            e.detail.shouldSwap = false;
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
            $("#table-" + es).DataTable().ajax.reload(function(){
                htmx.process("#table-" + es);
            },false);
            $("#table-" + es).DataTable().on( 'draw.dt', function () {
                htmx.process("#table-" + es);
                $("body").busyLoad("hide", {
                    animation: "fade"
                });
            });
            history.pushState({}, null, detailRefererPathSub);
        };
        // if (e.detail.target.id == addFormBlockSubID && !e.detail.xhr.response) {
        //     // Başarılı yanıt geldiğinde mesajı görüntüleyin
        //     if (e.detail.xhr.status === 204) {
        //         console.log("#message-container-" + ee + "-" + ei);
        //         $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
        //         // Mesajı belirli bir süre sonra gizle
        //         console.log("eburasıu");
        //         setTimeout(function() {
        //           $("#message-container-inside-" + ee + "-" + ei).fadeOut("slow");
        //         }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
        //     };
        // };
    });
    //cancelled
    htmx.on("hidden.bs.modal", (e) => {
        if (e.target.id == "addFormBlock-inform-d-justDetail-" + es) {
            document.getElementById("addFormBlock-inform-d-justDetail-" + es).innerHTML = "";
        };
    });
  
};

$(document).ready(function () {
    setNavTabSubRoom();
});


function formSubmitMessageWarehouse(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
    
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
      console.log(ee + ei);
      event.preventDefault();
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
              console.log("#message-container-" + ee + "-" + ei);
                $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                console.log("eburasıu");
                setTimeout(function() {
                  $("#message-container-inside-" + ee + "-" + ei).fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            };
        },
        error: function (xhr, status, error) {
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
        }
      });
      
    });
  
    $("#form-" + ee +  "-" + ei + "-add-3").submit(function (event) {
      event.preventDefault();
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
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
            
                  let eSub = ee +  "-" + ei + "-add-3";
            
                  let navTagSub = $("#navTag-" + eSub);
                  let tabPaneSub = $("#tabPane-" + eSub);
            
                  navTagSub.prev().children("a").addClass("active");
                  tabPaneSub.prev().addClass("show active");
                  
                  navTagSub.prev().children("a").children("button").show();
                  $("#table-" + ee).DataTable().columns.adjust();
                  
                  navTagSub.remove();
                  tabPaneSub.remove();
            
                  setTimeout(function() {
                    $("body").busyLoad("hide", {
                      animation: "fade"
                    });
                  }, 1000);
            
                }, 2000);
                $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                console.log("eburasıu");
                setTimeout(function() {
                  $("#message-container-inside-" + ee + '-' + ei + "-add-3").fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            }
        },
        error: function (xhr, status, error) {
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
        }
      });
      
  
      
  
    });
};

function setNavTabSubWarehouse(){
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

// var options = []
    
// fetch('/data/api/parts?maker=' + maker + '&type=' + type + '&format=datatables', {method : "GET"})
//   .then((response) => {
//   return response.json();
//   })
//   .then((data) => {
//     console.log(data["data"][0]["id"]);
//     for(let i = 0; i < data["data"].length; i++){
//       options.push({label : data["data"][i]["partNo"] + " - " + data["data"][i]["description"], value : data["data"][i]["id"]})
//     };

//     setWarehousePartDetailDatatable();
    
// });

$(document).ready(function () {
    //setHTMX();
    setNavTabSubWarehouse();
    formSubmitMessageWarehouse();
    
});
function setNavTabPurchasingPurchaseOrder(){
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

function setNavTabSubDetailPurchasingPurchaseOrderAdd(){
    let eSub = elementTag + "-" + elementTagId + "-add-2";
  
    if(elementTag == "quotationAdd"){
      var efSub = "inquiry";
    }else if(elementTag == "inquiryAdd"){
      var efSub = "request";
    }else if(elementTag == "orderConfirmationAdd"){
        var efSub = "orderConfirmation";
    }else if(elementTag == "purchaseOrderAdd"){
        var efSub = "purchaseOrder";
    }else if(elementTag == "purchasingPurchaseOrderAdd"){
        var efSub = "purchasingPurchaseOrder";
    };
    
    let uSub = pageUrl;
    
    let navTagSub = $("#navTag-" + eSub);
    let navTagLinkSub = $("#navTagLink-" + eSub);
    let tabPaneSub = $("#tabPane-" + eSub);
    let removeNavSub = $("#removeNav-" + eSub);
    let sideBarButtonSub = $(".nav-list li ." + eSub);
  
    $(".mainNavLinkSubDetail-" + efSub).removeClass("active");
    $(".mainTabPaneSubDetail-" + efSub).removeClass("show active");
  
    $("#nav-" + efSub + "-" + elementTagId + "-add").append(navTagSub);
    $("#tab-" + efSub + "-" + elementTagId + "-add").append(tabPaneSub);
    navTagLinkSub.addClass("active");
    tabPaneSub.addClass("show active");
  
    $(".mainNavLinkSubDetail:not(.active)").children("button").hide();
  
    removeNavSub.click(function(){
      navTagSub.prev().children("a").addClass("active");
      //tabPaneSub.prev().addClass("show active");
      $("#tabPane-" + efSub + "-" + elementTagId + "-add-1").addClass("show active");
      console.log(tabPaneSub);
      
      navTagSub.prev().children("a").children("button").show();
      
      navTagSub.remove();
      tabPaneSub.remove();
  
      sideBarButtonSub.attr("hx-swap", "afterbegin");
  
      $("#createQuotationButton").removeClass("d-none");
        
    });
  
    navTagLinkSub.on("shown.bs.tab", function(e){
        $(e.target).children("button").show();
        console.log($(e.target));
  
        $(e.relatedTarget).children("button").hide();
  
        history.pushState({}, null, uSub);
    });
  
    navTagSub.css({"display" : "block"});
};

function formSubmitMessagePurchasingPurchaseOrderAdd(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei + "-add-2").submit(function (event) {
        //spinner başlatır
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
      event.preventDefault();

      var formData = $(this).serializeArray();
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: formData,
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
                setTimeout(function() {
            
                    let eSub = ee +  "-" + ei + "-add-2";
                
                    let navTagSub = $("#navTag-" + eSub);
                    let tabPaneSub = $("#tabPane-" + eSub);
                
                    navTagSub.prev().children("a").addClass("active");
                    
                    navTagSub.prev().children("a").children("button").show();
                    $("#table-" + ee).DataTable().columns.adjust();
                    
                    navTagSub.remove();
                    tabPaneSub.remove();

                    addUpdateDataModalL.hide();
                    // $("#addUpdateDataModal-" + ee + "-" + ei).hide();
                    // $(".modal-backdrop").hide();

                    if($("#navTag-purchasingPurchaseOrder").length > 0){
                        $("#navTagLink-inquiry").removeClass("active");
                        $("#tabPane-inquiry").removeClass("active show");
                        $("#navTagLink-purchasingPurchaseOrder").addClass("active");
                        $("#tabPane-purchasingPurchaseOrder").addClass("active show");

                        fetch('/purchasing/api/purchase_orders?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                        .then((response) => {
                            return response.json();
                        })
                        .then((data) => {
                            htmx.ajax("GET", "/purchasing/purchase_order_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                            window.history.pushState({}, '', "/purchasing/purchase_order_update/" + data["data"][0]["id"] + "/");
                        });
                    }else{
                        htmx.ajax("GET", "/purchasing/purchase_order_data", {target:"#tabCont", swap:"afterbegin"});
                        setNavTabPurchaseOrder();
                        fetch('/purchasing/api/purchase_orders?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                        .then((response) => {
                            return response.json();
                        })
                        .then((data) => {
                            htmx.ajax("GET", "/purchasing/purchase_order_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                            window.history.pushState({}, '', "/purchasing/purchase_order_update/" + data["data"][0]["id"] + "/");
                        });
                    };
            
                  setTimeout(function() {
                    $("body").busyLoad("hide", {
                      animation: "fade"
                    });
                  }, 1500);
            
                }, 2000);
                $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                setTimeout(function() {
                  $("#message-container-inside-" + ee + '-' + ei + "-add-2").fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            }
        },
        error: function (xhr, status, error) {
            //spinner durdurur
            $("body").busyLoad("hide", {
                animation: "fade"
              });
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-xmark-circle me-1"></i>At least one part must be selected!</div>');
        }
      });
      
  
      
  
    });
};

$(document).ready(function () {
    //setNavTabPurchaseOrder();
    setNavTabSubDetailPurchasingPurchaseOrderAdd();
    //formSubmitMessagePurchaseOrderAdd();
});
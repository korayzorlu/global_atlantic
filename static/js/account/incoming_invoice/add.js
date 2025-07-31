function setNavTabIncomingInvoice(){
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

function setNavTabSubIncomingInvoice(){
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

function formSubmitMessageIncomingInvoiceAdd(){
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

                        addUpdateDataModal.hide();
                        addUpdateDataModalXl.hide();
                        //$(".modal-backdrop").hide();

                        if($("#navTag-incomingInvoice").length > 0){
                            $("#navTagLink-orderInProcessA").removeClass("active");
                            $("#tabPane-orderInProcessA").removeClass("active show");
                            $("#navTagLink-incomingInvoice").addClass("active");
                            $("#tabPane-incomingInvoice").addClass("active show");

                            fetch('/account/api/incoming_invoices?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                            .then((response) => {
                                return response.json();
                            })
                            .then((data) => {
                                htmx.ajax("GET", "/account/incoming_invoice_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                                window.history.pushState({}, '', "/account/incoming_invoice_update/" + data["data"][0]["id"] + "/");
                            });
                        }else{
                            htmx.ajax("GET", "/account/incoming_invoice_data", {target:"#tabCont", swap:"afterbegin"});
                            setNavTabIncomingInvoice();
                            fetch('/account/api/incoming_invoices?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                            .then((response) => {
                                return response.json();
                            })
                            .then((data) => {
                                htmx.ajax("GET", "/account/incoming_invoice_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                                window.history.pushState({}, '', "/account/incoming_invoice_update/" + data["data"][0]["id"] + "/");
                            });
                        };
                
                    setTimeout(function() {
                        $("#table-orderInProcessA").DataTable().ajax.reload(function() {
                            htmx.process("#table-orderInProcessA"); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
                        }, false);
                        $("body").busyLoad("hide", {
                        animation: "fade"
                        });
                    }, 1500);
                
                    }, 2000);
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
            let eSub = "incomingInvoice-new";

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

            
            
            fetch('/account/api/incoming_invoices?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                .then((response) => {
                return response.json();
                })
                .then((data) => {
                console.log(data["data"][0]["id"]);
                htmx.ajax("GET", "/account/incoming_invoice_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                window.history.pushState({}, '', "/account/incoming_invoice_update/" + data["data"][0]["id"] + "/");
                
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
    setNavTabSubIncomingInvoice();
    formSubmitMessageIncomingInvoiceAdd();
});
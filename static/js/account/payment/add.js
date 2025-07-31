function select2PaymentAdd(){
  $('#formOutline-payment-customer').select2({
      ajax: {
        url: "/account/payment_add/",
        dataType: 'json',
        delay: 250,
        data: function (params) {
          return {
            term: params.term,  // Arama terimi
            type: 'company'    // Hangi select2 için olduğunu belirtmek için 'type' parametresi
          };
        },
        escapeMarkup: function (markup) { return markup; },
        processResults: function (data) {
          return {
          results: $.map(data, function (item) {
              // tek satırda koşul sorgulamak için; sorgu ? koşul sağlanıyorsa değer : koşul sağlanmıyorsa değer
              text = `
                  <span>${item.name}</span>
              `
              return {id: item.id,
                      name: item.name ? item.name : "---"
                  };
            })
          };
        }
      },
      escapeMarkup: function (markup) { return markup; }, // HTML işleme için escape yapmıyoruz
      templateResult: function (data) {
          if (!data.id) { 
              return data.text;
          }

          // Burada özel HTML şablonunu oluşturun
          var markup = `
              <span>${data.name}</span>
          `;
          return markup;
          },
          templateSelection: function (data) {
            if(data.id){
              var markup = `${data.text}`;
            }else{
              var markup = "Search for a company";
            };
            
            return markup;
      },
      minimumInputLength: 3,
      placeholder: "Search for a company",
      allowClear: true,
      closeOnSelect: true,
      minimumResultsForSearch: Infinity,
      scrollAfterSelect: true,
      width: "100%",
      dropdownCssClass: "paymentSelect2"
  });


  $(".paymentSelect2 .select2-results__option.select2-results__option--selectable").css({"font-size":"6px"});


  $('#formOutline-payment-sourceBank').select2({
    ajax: {
      url: "/account/payment_add/",
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return {
          term: params.term,  // Arama terimi
          type: 'bank'    // Hangi select2 için olduğunu belirtmek için 'type' parametresi
        };
      },
      escapeMarkup: function (markup) { return markup; },
      processResults: function (data) {
        return {
          results: $.map(data, function (item) {
              // tek satırda koşul sorgulamak için; sorgu ? koşul sağlanıyorsa değer : koşul sağlanmıyorsa değer
              text = `
                  <span>${item.bankName}</span>
              `
              return {id: item.id,
                      bankName: item.bankName ? item.bankName : "---",
                      ibanNo: item.ibanNo ? item.ibanNo : "---",
                      currency: item.currency__code ? item.currency__code : "---"
                  };
          })
        };
      }
    },
    escapeMarkup: function (markup) { return markup; }, // HTML işleme için escape yapmıyoruz
    templateResult: function (data) {
        if (!data.id) { 
            return data.text;
        }

        // Burada özel HTML şablonunu oluşturun
        var markup = `
            <div class='p-0 m-0 border-bottom'>
                    <table class="no-footer p-0 m-0" style="width:100%;">
                        <thead>
                            <tr>
                                <td style="width:50%; font-weight:bold;">Bank Account</td>
                                <td style="width:40%; font-weight:bold;">IBAN</td>
                                <td style="width:10%; font-weight:bold;">Currency</td>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>${data.bankName}</td>
                                <td>${data.ibanNo}</td>
                                <td>${data.currency}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
        `;
        return markup;
    },
    templateSelection: function (data) {
        if(data.id){
          var markup = `${data.text}`;
        }else{
          var markup = "Search for a bank";
        };
        
        return markup;
    },
    //minimumInputLength: 3,
    placeholder: "Search for a bank",
    allowClear: true,
    closeOnSelect: true,
    minimumResultsForSearch: 1,
    scrollAfterSelect: true,
    width: "100%",
    dropdownCssClass: "bankSelect2"
  });

  $(".bankSelect2 .select2-results").css({"max-height":"600px"});
  $(".bankSelect2 .select2-results__option.select2-results__option--selectable").css({"font-size":"6px"});
  
};

function setNavTabSubPaymentAdd(){
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

// function setNavTabSubPayment(){
//     let eSub = elementTag + "-" + elementTagId;
//     let efSub = elementTag;
//     let uSub = pageUrl;
  
//     let navTagSub = $("#navTag-" + eSub);
//     let navTagLinkSub = $("#navTagLink-" + eSub);
//     let tabPaneSub = $("#tabPane-" + eSub);
//     let removeNavSub = $("#removeNav-" + eSub);
//     let sideBarButtonSub = $(".nav-list li ." + eSub);
  
//     if($("#navTag-" + eSub + ".hereOn").length > 0){
//       $("#navTag-" + eSub + ".hereOn").remove();
//       $("#tabPane-" + eSub + ".hereOn").remove();
  
//       $("#navTag-" + eSub).addClass("hereOn");
//       $("#tabPane-" + eSub).addClass("hereOn");
  
//       $(".mainNavLinkSub-" + efSub).removeClass("active");
//       $(".mainTabPaneSub-" + efSub).removeClass("show active");
  
//       $("#tabNavSub-" + efSub).append(navTagSub);
//       $("#tabContSub-" + efSub).append(tabPaneSub);
//       navTagLinkSub.addClass("active");
//       tabPaneSub.addClass("show active");
  
//       $(".mainNavLinkSub:not(.active)").children("button").hide();
//       $("#navTag-" + eSub).children("a").children("button").show();
//       $("#table-" + eSub).DataTable().columns.adjust();
  
//       removeNavSub.click(function(){
//         navTagSub.prev().children("a").addClass("active");
//         tabPaneSub.prev().addClass("show active");
//         navTagSub.prev().children("a").children("button").show();
//         $("#table-" + efSub).DataTable().columns.adjust();
//         navTagSub.remove();
//         tabPaneSub.remove();
//         sideBarButtonSub.attr("hx-swap", "afterbegin");
//       });
  
//       navTagLinkSub.on("shown.bs.tab", function(e){
//         $(e.target).children("button").show();
//         $(e.relatedTarget).children("button").hide();
//         $("#table-" + efSub).DataTable().columns.adjust();
//         $("#table-" + eSub).DataTable().columns.adjust();
//         history.pushState({}, null, uSub);
//       });
  
//       navTagSub.css({"display" : "block"});
  
//       document.querySelectorAll('.form-outline').forEach((formOutline) => {
//         new mdb.Input(formOutline).update();
//       });
      
//     }else{
//       $("#navTag-" + eSub).addClass("hereOn");
//       $("#tabPane-" + eSub).addClass("hereOn");
  
//       $(".mainNavLinkSub-" + efSub).removeClass("active");
//       $(".mainTabPaneSub-" + efSub).removeClass("show active");
  
//       $("#tabNavSub-" + efSub).append(navTagSub);
//       $("#tabContSub-" + efSub).append(tabPaneSub);
//       navTagLinkSub.addClass("active");
//       tabPaneSub.addClass("show active");
  
//       $(".mainNavLinkSub:not(.active)").children("button").hide();
  
//       $("#table-" + eSub).DataTable().columns.adjust();
  
//       console.log(removeNavSub);
//       removeNavSub.click(function(){
//         navTagSub.prev().children("a").addClass("active");
//         tabPaneSub.prev().addClass("show active");
//         navTagSub.prev().children("a").children("button").show();
//         $("#table-" + efSub).DataTable().columns.adjust();
//         navTagSub.remove();
//         tabPaneSub.remove();
//         sideBarButtonSub.attr("hx-swap", "afterbegin");
//       });
  
//       navTagLinkSub.on("shown.bs.tab", function(e){
//           $(e.target).children("button").show();
//           $(e.relatedTarget).children("button").hide();
//           $("#table-" + efSub).DataTable().columns.adjust();
//           $("#table-" + eSub).DataTable().columns.adjust();
//           history.pushState({}, null, uSub);
//       });
  
//       navTagSub.css({"display" : "block"});
  
//       document.querySelectorAll('.form-outline').forEach((formOutline) => {
//         new mdb.Input(formOutline).update();
//       });
      
//     };
// };



function formSubmitMessagePaymentAdd(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
      event.preventDefault();

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
        /**/let eSub = "payment-new";
            let u = pageUrl;

            let navTagSub = $("#navTag-" + eSub);
            let tabPaneSub = $("#tabPane-" + eSub);

            navTagSub.prev().children("a").addClass("active");
            tabPaneSub.prev().addClass("show active");
            
            navTagSub.prev().children("a").children("button").show();
            $("#table-" + ee).DataTable().columns.adjust();
            
            navTagSub.remove();
            tabPaneSub.remove();

            // fetch('/account/api/payments?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
            //   .then((response) => {
            //     return response.json();
            //   })
            //   .then((data) => {
            //     console.log(data["data"][0]["id"]);
            //     htmx.ajax("GET", "/account/payment_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
            //     window.history.pushState({}, '', "/account/payment_update/" + data["data"][0]["id"] + "/");
            
            //   })
            
            setTimeout(function() {
                $("body").busyLoad("hide", {
                animation: "fade"
                });
            }, 1000);
        

        }, 2000);
      
    });
};



$(document).ready(function () {
    select2PaymentAdd();
    //setHTMX();
    setNavTabSubPaymentAdd();
    //formSubmitMessagePaymentAdd();
    //paymentAddWebSocket();
});

function setInquiryDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag;

    //tablo oluşurken loading spinner'ını açar
    $("#tabPane-" + ef).busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: window.getComputedStyle($(".tab-content")[0]).backgroundColor,
      color: "#455359",
      textColor: "#455359"
    });

    let addFormBlockID = "#addFormBlock-" + ef;
    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);
/**/let addDataHxGet = "/sale/inquiry_add/";
    let addDataHxTarget = addFormBlockID;

    let order = [[2, 'desc']];
  
    let buttons = [
        // {
        //   text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        //   }
        // },
        {
          // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/deletefile.svg"},
          className: "deleteData tableTopButtons inTableButtons delete-" + ef + ""
        },
        // {
        //   extend: "csvHtml5",
        //   // text: '<i class="fa-solid fa-file-csv" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to csv file"></i>',
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/csv-file.svg"},
        //   className: "tableTopButtons inTableButtons",
        // },
        // {
        //   extend: "excelHtml5",
        //   // text: '<i class="fa-solid fa-file-excel" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to excel file"></i>',
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/xls.svg"},
        //   className: "tableTopButtons inTableButtons",
        // },
        // {
        //   extend: "pdfHtml5",
        //   // text: '<i class="fa-solid fa-file-pdf" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to pdf file"></i>',
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/pdf.svg"},
        //   className: "tableTopButtons inTableButtons",
        // },
        // {
        //   extend: "print",
        //   // text: '<i class="fa-solid fa-print" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Print"></i>',
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/printer.svg"},
        //   className: "tableTopButtons inTableButtons",
        // },
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
          className: "tableTopButtons inTableButtons",
          action: function ( e, dt, node, config ) {
            $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("show", {
              animation: false,
              spinner: "pulsar",
              maxSize: "150px",
              minSize: "150px",
              text: "Loading ...",
              background: "rgba(69, 83, 89, 0.6)",
              color: "#455359",
              textColor: "#fff"
            });

            table.DataTable().ajax.reload(function() {
              
            });
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];
  
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/sale/inquiry_delete/";
    let serverSide = true;
/**/let apiSource = '/sale/api/inquiries?format=datatables';
/**/let columns = [
                    {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable", "visible":false},
                    {"data" : "projectNo", className:"double-clickable ps-1 pe-1"},
                    {"data" : "inquiryNo", className:"double-clickable ps-1 pe-1" , render: function (data, type, row, meta)
                        {return '<a hx-get="/sale/inquiry_update/' + row.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                        //return '<a href="/card/company_update/' + row.id + '/" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                    },
                    {"data" : "inquiryDate", className:"double-clickable ps-1 pe-1"},
                    {"data" : "customer", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "vessel", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "supplier", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "supplierRef", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "maker", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "makerType", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "projectCreator", className:"double-clickable ps-1 pe-1"},
                    {"data" : "projectStage", className:"double-clickable shadow-0 ps-1 pe-1", "width" : "9%", render: function (data, type, row, meta){
                      if(data == "request"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="secondary" style="padding:2px 5px;margin:0;"><i class="fas fa-sheet-plastic me-3"></i>Request</div>';
                      }else if(data == "inquiry"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="secondary" style="padding:2px 5px;margin:0;"><i class="fas fa-magnifying-glass-dollar me-3"></i>Inquiry</div>';
                      }else if(data == "quotation"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="secondary" style="padding:2px 5px;margin:0;"><i class="fas fa-file-invoice-dollar me-3"></i>Quotation</div>';
                      }else if(data == "order_confirmation"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="primary" style="padding:2px 5px;margin:0;"><i class="fas fa-file-invoice-dollar me-3"></i>Order Confirmed</div>';
                      }else if(data == "order_not_confirmation"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="danger" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-question me-3"></i>Order Rejected</div>';
                      }else if(data == "purchase_order"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="primary" style="padding:2px 5px;margin:0;"><i class="fas fa-money-bill-1 me-3"></i>Purchase Order</div>';
                      }else if(data == "order_tracking"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="warning" style="padding:2px 5px;margin:0;"><i class="fas fa-plane-departure me-3"></i>Order Tracking</div>';
                      }else if(data == "invoiced"){
                        return '<div class="alert text-start" role="alert" data-mdb-color="success" style="padding:2px 5px;margin:0;"><i class="fas fa-file-invoice-dollar me-3"></i>Invoiced</div>';
                      }
                    }
                    }
    ];

    table.DataTable({
      order : order,
      "serverSide" : serverSide,
      "processing" : true,
      "autoWidth": true,
      select: {
        style: 'single',
        selector: 'td:first-child'
      },
      "pageLength": 50,
      scrollY : "77vh",
      scrollCollapse: true,
      colReorder: true,
      fixedHeader: {
        header: true,
        headerOffset: $('#fixed').height()
      },
      responsive : false,
      language: { search: '', searchPlaceholder: "Search..." },
      dom : 'Blfrtip',
      buttons : buttons,
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      initComplete: function () {
        $(tableId + '_wrapper div.dataTables_filter input').focus();
      },
      createdRow: function(row, data, index) {
        var projectStage = data.projectStage;
        if(projectStage == "request" || projectStage == "inquiry" || projectStage == "quotation"){
          $('td:eq(12)', row).addClass("tableAlert-secondary");
        }else if(projectStage == "order_confirmation" || projectStage == "purchase_order"){
          $('td:eq(12)', row).addClass("tableAlert-primary");
        }else if(projectStage == "order_tracking"){
          $('td:eq(12)', row).addClass("tableAlert-warning");
        }else if(projectStage == "invoiced"){
          $('td:eq(12)', row).addClass("tableAlert-success");
        };
      },
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>td></td><td></td><td></td><td></td><td></td></tr>"));
        }
      },
      "ajax" : apiSource,
      "columns" : columns
    });

  
    new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);

    /////////////tabloya Özel/////////////
    //MDB Alert'lerin çalışması için
    var alerts = document.querySelectorAll(".alert");
        for (var i = 0; i < alerts.length; i++) {
          var alert = alerts[i];
          new mdb.Alert(alert);
    };
    /////////////tabloya Özel-end/////////////
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        /////////////tabloya Özel/////////////
        //MDB Alert'lerin çalışması için
        var alerts = document.querySelectorAll(".alert");
            for (var i = 0; i < alerts.length; i++) {
              var alert = alerts[i];
              new mdb.Alert(alert);
        };
        /////////////tabloya Özel-end/////////////
        //tablo oluştuğunda loading spinner'ını kapatır
        $("#tabPane-" + ef).busyLoad("hide", {
          animation: "fade"
        });

        //sıra numaralarını ekler
        let j = 1;
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(j++);
        });

    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/inquiry_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/inquiry_update/' + data["id"] + '/');
    });

    //select all işlemi event'i
    $('#select-all-' + ef).on( "click", function(e) {
      if ($(this).is( ":checked" )) {
          table.DataTable().rows().select();        
      } else {
          table.DataTable().rows().deselect(); 
      }
    });
    
    //veri silme butonu
    if(deleteDataButton){
        $(deleteDataButtonId).click(function (){
            
            let idList = []
            for(let i = 0; i < table.DataTable().rows({selected:true}).data().length; i++){
                idList.push(table.DataTable().rows({selected:true}).data()[i]["id"]);
            };
            htmx.ajax("GET", deleteDataUrl + idList, "#addUpdateDataDialog");
            console.log(idList);
        });
    };
    
    //tabloyu sağa ve sola yaslamak için parent elementin paddingini kaldır
    $('.box:has(' + tableId + '_wrapper)').css({
      'padding': '12px 0'
    });

    //tablo uznluğu seçimindeki yazıları kaldırır
    $("div.dataTables_wrapper div.dataTables_length label").contents().filter(function() {
      return this.nodeType === 3 && (this.nodeValue.includes("Show") || this.nodeValue.includes("entries"));
    }).remove();

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

};

function setNavTabInquiry(){
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
};

function setNavTabSubInquiry(){
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

function setHTMXInquiry(){
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
  /**/setInquiryDataTable();
  setNavTabInquiry();
  setNavTabSubInquiry();
  setHTMXInquiry();
  //formSubmitMessage();

});
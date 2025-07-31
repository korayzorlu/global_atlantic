function setFinancialReportOrderDataTable(){/**/
    

    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-order";

    //tablo oluşurken loading spinner'ını açar
    $("#tabPane-" + elementTag).busyLoad("show", {
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
  
    let buttons = [
        {
          tag: "img",
          attr: {src:"/static/images/icons/datatable/pdf.svg"}, 
          className: "tableTopButtons inTableButtons",
          action: function ( e, dt, node, config ) {
            htmx.ajax("GET", "/report/financial_report_filter_pdf", {target : "#addUpdateDataDialogL"});
          }
        },
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
          className: "tableTopButtons inTableButtons",
          action: function ( e, dt, node, config ) {
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

            table.DataTable().ajax.reload(function() {
              
            });
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $("body").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        },
        {
          tag: "button",
          attr: {type:"button"}, 
          className: "btn btn-danger bg-blue-esms text-white ms-auto financialReportFilterActive",
          text: "Today",
          action: function ( e, dt, node, config ) {
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

            var day = new Date().getDate();
            var month = new Date().getMonth() + 1;
            var year = new Date().getFullYear();
            var today = day + "/" + month + "/" + year;

            $('#startDateTable').val(today)
            $('#endDateTable').val(today)

            $(e.currentTarget).removeClass("bg-red-esms");
            $(e.currentTarget).addClass("bg-blue-esms");
            $(".financialReportFilterActive").removeClass("bg-blue-esms");
            $(".financialReportFilterActive").addClass("bg-red-esms");
            $(".financialReportFilterActive").removeClass("financialReportFilterActive");
            $(e.currentTarget).addClass("financialReportFilterActive");
            $("#table-financialReport-order").DataTable().ajax.url('/report/api/financial_report_orders?startdate='+today+'&enddate='+today+'&format=datatables').load();
            $("#table-financialReport-sendInvoice").DataTable().ajax.url( '/report/api/financial_report_send_invoices?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-incomingInvoice").DataTable().ajax.url( '/report/api/financial_report_incoming_invoices?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-paymentIn").DataTable().ajax.url( '/report/api/financial_report_payment_ins?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-paymentOut").DataTable().ajax.url( '/report/api/financial_report_payment_outs?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankHalkbank").DataTable().ajax.url( '/report/api/financial_report_bank_halkbanks?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankVakifbank").DataTable().ajax.url( '/report/api/financial_report_bank_vakifbanks?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankIsbank").DataTable().ajax.url( '/report/api/financial_report_bank_isbanks?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankAlbarakaturk").DataTable().ajax.url( '/report/api/financial_report_bank_albarakaturks?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankEmlakkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_emlakkatilims?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankVakifkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_vakifkatilims?startdate='+today+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankZiraatkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_ziraatkatilims?startdate='+today+'&enddate='+today+'&format=datatables' ).load();

            $("#table-financialReport-order").on( 'draw.dt', function () {
              htmx.process(tableId);
              $("body").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        },
        // {
        //   tag: "button",
        //   attr: {type:"button"}, 
        //   className: "btn btn-danger bg-red-esms text-white ms-auto",
        //   text: "30  Day",
        //   action: function ( e, dt, node, config ) {
        //     htmx.ajax("GET", "/sale/report_filter_pdf", {target : "#addUpdateDataDialogXl"});
        //   }
        // },
        {
          tag: "button",
          attr: {type:"button"}, 
          className: "btn btn-danger bg-red-esms text-white ms-auto",
          text: "All",
          action: function ( e, dt, node, config ) {
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

            var day = new Date().getDate();
            var month = new Date().getMonth() + 1;
            var year = new Date().getFullYear();
            var today = day + "/" + month + "/" + year;
            var yearday = "1/1/2024";

            $('#startDateTable').val(yearday)
            $('#endDateTable').val(today)

            $(e.currentTarget).removeClass("bg-red-esms");
            $(e.currentTarget).addClass("bg-blue-esms");
            $(".financialReportFilterActive").removeClass("bg-blue-esms");
            $(".financialReportFilterActive").addClass("bg-red-esms");
            $(".financialReportFilterActive").removeClass("financialReportFilterActive");
            $(e.currentTarget).addClass("financialReportFilterActive");
            $("#table-financialReport-order").DataTable().ajax.url('/report/api/financial_report_orders?startdate='+yearday+'&enddate='+today+'&format=datatables').load();
            $("#table-financialReport-sendInvoice").DataTable().ajax.url( '/report/api/financial_report_send_invoices?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-incomingInvoice").DataTable().ajax.url( '/report/api/financial_report_incoming_invoices?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-paymentIn").DataTable().ajax.url( '/report/api/financial_report_payment_ins?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-paymentOut").DataTable().ajax.url( '/report/api/financial_report_payment_outs?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankHalkbank").DataTable().ajax.url( '/report/api/financial_report_bank_halkbanks?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankVakifbank").DataTable().ajax.url( '/report/api/financial_report_bank_vakifbanks?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankIsbank").DataTable().ajax.url( '/report/api/financial_report_bank_isbanks?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankAlbarakaturk").DataTable().ajax.url( '/report/api/financial_report_bank_albarakaturks?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankEmlakkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_emlakkatilims?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankVakifkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_vakifkatilims?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();
            $("#table-financialReport-bankZiraatkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_ziraatkatilims?startdate='+yearday+'&enddate='+today+'&format=datatables' ).load();

            $("#table-financialReport-order").on( 'draw.dt', function () {
              htmx.process(tableId);
              $("body").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        },
        // {
        //   tag: "div",
        //   attr: {}, 
        //   className: "btn border-0 shadow-0 bg-white pb-0",
        //   text: `<div class="form-outline datepicker pb-2 d-none" id="startDatePickerTable">
        //             <input type="text" id="startDateTable" class="form-control form-control-sm">
        //             <label for="startDateTable" class="form-label">Start Date</label>
        //         </div>`,
        //   action: function ( e, dt, node, config ) {

        //   }
        // },
    ];

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_orders?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "orderConfirmationAmount"){
                        return "ORDER AMOUNT"
                      }else if(data == "purchaseOrderAmount"){
                        return "PO AMOUNT"
                      }else if(data == "balanceAmount"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : 'B',
      buttons : buttons,
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);

        //tablo oluştuğunda loading spinner'ını kapatır
        $("#tabPane-" + elementTag).busyLoad("hide", {
          animation: "fade"
        });

    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });

    //////////////////Tabloya Özel/////////////////
    //tarih değişikliği event
    $('#startDatePickerTableBlock').on("dateChange.mdb.datepicker", function(){
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

      var startday = $('#startDateTable').val()
      var endday = $('#endDateTable').val()

      $(".financialReportFilterActive").addClass("bg-red-esms");
      $(".financialReportFilterActive").removeClass("financialReportFilterActive");
      $("#table-financialReport-order").DataTable().ajax.url('/report/api/financial_report_orders?startdate='+startday+'&enddate='+endday+'&format=datatables').load();
      $("#table-financialReport-sendInvoice").DataTable().ajax.url( '/report/api/financial_report_send_invoices?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-incomingInvoice").DataTable().ajax.url( '/report/api/financial_report_incoming_invoices?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-paymentIn").DataTable().ajax.url( '/report/api/financial_report_payment_ins?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-paymentOut").DataTable().ajax.url( '/report/api/financial_report_payment_outs?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankHalkbank").DataTable().ajax.url( '/report/api/financial_report_bank_halkbanks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankVakifbank").DataTable().ajax.url( '/report/api/financial_report_bank_vakifbanks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankIsbank").DataTable().ajax.url( '/report/api/financial_report_bank_isbanks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankAlbarakaturk").DataTable().ajax.url( '/report/api/financial_report_bank_albarakaturks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankEmlakkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_emlakkatilims?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankVakifkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_vakifkatilims?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankZiraatkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_ziraatkatilims?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();

      $("#table-financialReport-order").on( 'draw.dt', function () {
        htmx.process(tableId);
        $("body").busyLoad("hide", {
          animation: "fade"
        });
      });
    });

    $('#endDatePickerTableBlock').on("dateChange.mdb.datepicker", function(){
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

      var startday = $('#startDateTable').val()
      var endday = $('#endDateTable').val()

      $(".financialReportFilterActive").addClass("bg-red-esms");
      $(".financialReportFilterActive").removeClass("financialReportFilterActive");
      $("#table-financialReport-order").DataTable().ajax.url('/report/api/financial_report_orders?startdate='+startday+'&enddate='+endday+'&format=datatables').load();
      $("#table-financialReport-sendInvoice").DataTable().ajax.url( '/report/api/financial_report_send_invoices?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-incomingInvoice").DataTable().ajax.url( '/report/api/financial_report_incoming_invoices?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-paymentIn").DataTable().ajax.url( '/report/api/financial_report_payment_ins?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-paymentOut").DataTable().ajax.url( '/report/api/financial_report_payment_outs?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankHalkbank").DataTable().ajax.url( '/report/api/financial_report_bank_halkbanks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankVakifbank").DataTable().ajax.url( '/report/api/financial_report_bank_vakifbanks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankIsbank").DataTable().ajax.url( '/report/api/financial_report_bank_isbanks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankAlbarakaturk").DataTable().ajax.url( '/report/api/financial_report_bank_albarakaturks?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankEmlakkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_emlakkatilims?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankVakifkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_vakifkatilims?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();
      $("#table-financialReport-bankZiraatkatilim").DataTable().ajax.url( '/report/api/financial_report_bank_ziraatkatilims?startdate='+startday+'&enddate='+endday+'&format=datatables' ).load();

      $("#table-financialReport-order").on( 'draw.dt', function () {
        htmx.process(tableId);
        $("body").busyLoad("hide", {
          animation: "fade"
        });
      });
    });
    //////////////////Tabloya Özel-end/////////////////
    
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

function setFinancialReportSendInvoiceDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-sendInvoice";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_send_invoices?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "amount"){
                        return "AMOUNT"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportIncomingInvoiceDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-incomingInvoice";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_incoming_invoices?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "amount"){
                        return "AMOUNT"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportPaymentInDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-paymentIn";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_payment_ins?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "amount"){
                        return "AMOUNT"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportPaymentOutDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-paymentOut";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_payment_outs?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "amount"){
                        return "AMOUNT"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankHalkbankDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankHalkbank";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_halkbanks?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankVakifbankDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankVakifbank";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_vakifbanks?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankIsbankDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankIsbank";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_isbanks?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankAlbarakaturkDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankAlbarakaturk";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_albarakaturks?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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
function setFinancialReportBankEmlakkatilimDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankEmlakkatilim";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_emlakkatilims?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankVakifkatilimDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankVakifkatilim";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_vakifkatilims?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankZiraatkatilimDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankZiraatkatilim";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_ziraatkatilims?startdate=' + $('#startDateTable').val() + '&enddate=' + $('#endDateTable').val() + '&format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "transferBalance"){
                        return "TRANS. BALANCE"
                      }else if(data == "inAmount"){
                        return "IN"
                      }
                      else if(data == "outAmount"){
                        return "OUT"
                      }else if(data == "balance"){
                        return "BALANCE"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportBankTotalDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-bankTotal";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    let serverSide = true;
/**/let apiSource = '/report/api/financial_report_bank_totals?format=datatables';
/**/let columns = [
                    {"data" : "type", className:"text-start pt-1 pb-1", orderable: false, "width":"20%", render: function (data, type, row, meta){
                      if(data == "balance"){
                        return "ESMS"
                      };
                    }
                    },
                    {"data" : "usd", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "eur", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "try", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"},
                    {"data" : "rub", className:"text-end pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"20%"}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentOutUSDDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentOutUSD";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=out&currency__code=USD&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + row.bank + " account to " + data
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentOutEURDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentOutEUR";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=out&currency__code=EUR&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + row.bank + " account to " + data
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentOutTRYDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentOutTRY";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=out&currency__code=TRY&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + row.bank + " account to " + data
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentOutRUBDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentOutRUB";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=out&currency__code=RUB&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + row.bank + " account to " + data
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentInUSDDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentInUSD";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=in&currency__code=USD&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + data + " to " + row.bank + " account"
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentInEURDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentInEUR";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=in&currency__code=EUR&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + data + " to " + row.bank + " account"
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentInTRYDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentInTRY";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=in&currency__code=TRY&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + data + " to " + row.bank + " account"
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setFinancialReportDailyPaymentInRUBDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag + "-dailyPaymentInRUB";

    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);

    var day = new Date().getDate()
    var month = new Date().getMonth() + 1
    var year = new Date().getFullYear()

    var today = year + "-" + month + "-" + day

    var amountTotal = 0

    let serverSide = true;
/**/let apiSource = '/account/api/payments?type=in&currency__code=RUB&paymentDate=' + today + '&format=datatables';
/**/let columns = [
                    {"data" : "customer", className:"text-start pt-1 pb-1 ps-1 pe-1", orderable: false, "width":"80%", render: function (data, type, row, meta){
                      return "A transfer has been made from " + data + " to " + row.bank + " account"
                    }
                    },
                    {"data" : "amount", className:"text-end pt-1 pb-1 ps-1 pe-1", "width": "20%", render: function (data, type, row, meta){
                      return (data).toLocaleString('tr-TR', { minimumFractionDigits: 2 })
                    }
                    },
                    {"data" : "bank", className:"text-start pt-1 pb-1 ps-1 pe-1","visible":false}
    ];
    
    table.DataTable({
      order : false,
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
      dom : '',
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [{
        "defaultContent": "",
        "targets": "_all"
      }],
      createdRow: function(row, data, index) {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();

        amountTotal = amountTotal + data.amount
        
      },
      drawCallback: function() {
        $(tableId + ' tbody').append($("<tr><td class='text-end pt-1 pb-1 ps-1 pe-1'>TOTAL</td><td class='text-end pt-1 pb-1 ps-1 pe-1'>" + amountTotal.toLocaleString('tr-TR', { minimumFractionDigits: 2 }) + "</td></tr>"));
    },
      ajax: {
        url: apiSource 
      },
      "columns" : columns
    });
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/sale/quotation_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/sale/quotation_update/' + data["id"] + '/');
    });
    
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

function setNavTabFinancialReport(){
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

function setNavTabSubFinancialReport(){
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


$(document).ready(function () {
    setFinancialReportOrderDataTable();
    setFinancialReportSendInvoiceDataTable();
    setFinancialReportIncomingInvoiceDataTable();
    setFinancialReportPaymentInDataTable();
    setFinancialReportPaymentOutDataTable();
    setFinancialReportBankHalkbankDataTable();
    setFinancialReportBankVakifbankDataTable();
    setFinancialReportBankIsbankDataTable();
    setFinancialReportBankAlbarakaturkDataTable();
    setFinancialReportBankEmlakkatilimDataTable();
    setFinancialReportBankVakifkatilimDataTable();
    setFinancialReportBankZiraatkatilimDataTable();
    setFinancialReportBankTotalDataTable();
    setFinancialReportDailyPaymentOutUSDDataTable();
    setFinancialReportDailyPaymentOutEURDataTable();
    setFinancialReportDailyPaymentOutTRYDataTable();
    setFinancialReportDailyPaymentOutRUBDataTable();
    setFinancialReportDailyPaymentInUSDDataTable();
    setFinancialReportDailyPaymentInEURDataTable();
    setFinancialReportDailyPaymentInTRYDataTable();
    setFinancialReportDailyPaymentInRUBDataTable();
    setNavTabFinancialReport();
    setNavTabSubFinancialReport();
    formSubmitMessage();

    $("#tabPane-financialReport-table table.dataTable").css({"margin-top":"0px"})
    $("#tabPane-financialReport-table th").css({"padding":".3rem 1rem"});
    
    $('#table-financialReport-order_wrapper .dt-buttons').append($("#startDatePickerTableBlock"));
    $("#startDatePickerTable").removeClass("d-none");

    $('#table-financialReport-order_wrapper .dt-buttons').append($("#endDatePickerTableBlock"));
    $("#endDatePickerTable").removeClass("d-none");
    
    document.querySelectorAll('.form-outline').forEach((formOutline) => {
      new mdb.Input(formOutline).update();
    });
});







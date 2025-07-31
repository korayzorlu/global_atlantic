
function setSOADataTable(){/**/
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
/**/let addDataHxGet = "/card/company_add/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[3, 'asc']];
  
    let buttons = [
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          className: "tableTopButtons inTableButtons",
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
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
/**/let deleteDataUrl = "/card/company_delete/";
    let serverSide = true;
/**/let apiSource = '/card/api/currents/?format=datatables';
/**/let columns = [ 
                    {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable ps-1 pe-1", "visible" : false},
                    //{"data" : "company.name", className:"double-clickable"},
                    {"data" : "company", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      return '<a hx-get="/account/soa_update/' + row.companyId + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                    }
                    },
                    {"data" : "debt", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "credit", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                        return '<span class="totalPriceText">' + (row.debt - row.credit).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "currency", className:"double-clickable ps-1 pe-1"},
                    {"data" : "exchangeRate", className:"double-clickable ps-1 pe-1", "visible" : false},
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.debt * row.exchangeRate).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.credit * row.exchangeRate).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + ((row.debt - row.credit) * row.exchangeRate).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "companyId", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "companyRole", className:"double-clickable ps-1 pe-1", "visible":false, render: function (data, type, row, meta){
                      if(data.customer === true && data.supplier === false){
                          return "Customer"
                      } else if(data.customer === false && data.supplier === true){
                          return "Supplier"
                      } else if(data.customer === true && data.supplier === true){
                          return "Customer, Supplier"
                      } else{
                          return ""
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
        style: 'multi',
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
      language: {
        search: '',
        searchPlaceholder: "Search..."
        //processing: '<i class="fa fa-circle-notch fa-spin fa-3x fa-fw" style="z-index:99999;"></i>'
      },
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
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        //console.log(api.page());
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        };
        
      },
      "ajax" : apiSource,
      "columns" : columns
    });



    //new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);
    table.DataTable().columns.adjust();
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        
        //tablo oluştuğunda loading spinner'ını kapatır
        $("#tabPane-" + ef).busyLoad("hide", {
          animation: "fade"
        });

        //sıra numaralarını ekler
        let pageLength = table.DataTable().page.len();
        let page = table.DataTable().page();
        let i = 1 + (page * pageLength);
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });

    });

    table.on('click', 'tbody tr', function (cell) {

      //console.log(table.DataTable().cells(null,1));
   
      //console.log(tableClass.row(idx).data())
  });  

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
        let data = table.DataTable().row(this).data();
  
    /**/htmx.ajax('GET', '/account/soa_update/' + data["companyId"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
        window.history.pushState({}, '', addDataHxGet);
    });

    //select all işlemi event'i
    $('#select-all-' + ef).on( "click", function(e) {
      if ($(this).is( ":checked" )) {
          table.DataTable().rows().select();        
      } else {
          table.DataTable().rows().deselect(); 
      }
    });

    //tablodaki filtre
    // table.DataTable().columns().every( function() {
    //   var that = this;

    //   $('input', this.footer()).on('keyup change', function() {
    //       if (that.search() !== this.value) {
    //           that
    //               .search(this.value)
    //               .draw();
    //       }
    //   });
    // });
    
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

function setSOAFullHistoryDataTable(){/**/
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

    let tableId = '#table-' + ef + "-soaFullHistory";
    let table = $('#table-' + ef + "-soaFullHistory");
/**/let addDataHxGet = "/card/company_add/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[3, 'desc']];
  
    let buttons = [
        // {
        //   // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/add-file.svg"},
        //   action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, {target : addDataHxTarget, swap : "afterbegin", "push-url" : "true"});
        //     window.history.pushState({}, '', addDataHxGet);
        //   }
        // },
        // {
        //   // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
        //   className: "deleteData tableTopButtons inTableButtons delete-" + ef + "",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/deletefile.svg"},
        // },
        // {
        //   extend: "csvHtml5",
        //   // text: '<i class="fa-solid fa-file-csv" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to csv file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/csv-file.svg"},
        // },
        // {
        //   extend: "excelHtml5",
        //   // text: '<i class="fa-solid fa-file-excel" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to excel file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/xls.svg"},
        // },
        // {
        //   extend: "pdfHtml5",
        //   // text: '<i class="fa-solid fa-file-pdf" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to pdf file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/pdf.svg"},
        // },
        // {
        //   extend: "print",
        //   // text: '<i class="fa-solid fa-print" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Print"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/printer.svg"},
        // },
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          className: "tableTopButtons inTableButtons",
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
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
/**/let deleteDataUrl = "/account/process_delete/";
    let serverSide = true;
/**/let apiSource = '/account/api/processes/?format=datatables';
/**/let columns = [ 
                    {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable ps-1 pe-1"},
                    {"data" : "processDateTime", className:"double-clickable ps-1 pe-1"},
                    {"data" : "type", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "send_invoice"){
                        return "SEND INVOICE";
                      }else if(row.type == "incoming_invoice"){
                        return "INCOMING INVOICE";
                      }else if(row.type == "payment_in"){
                        return "PAYMENT IN";
                      }else if(row.type == "payment_out"){
                        return "PAYMENT OUT";
                      }else{
                        return "";
                      };
                    }
                    },
                    //{"data" : "company.name", className:"double-clickable"},
                    {"data" : "company", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      return '<a hx-get="/account/soa_update/' + row.company.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                    }
                    },
                    {"data" : "sourceNo", className:"double-clickable ps-1 pe-1"},
                    {"data" : "amount", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "send_invoice"){
                        return '<span class="totalPriceText">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                      }else if(row.type == "incoming_invoice"){
                        return '<span class="totalPriceText">-' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                      }else if(row.type == "payment_in"){
                        return '';
                      }else if(row.type == "payment_out"){
                        return '';
                      }else{
                        return "";
                      };
                    }
                    },
                    {"data" : "amount", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "send_invoice"){
                        return '';
                      }else if(row.type == "incoming_invoice"){
                        return '';
                      }else if(row.type == "payment_in"){
                        return '<span class="totalPriceText">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                      }else if(row.type == "payment_out"){
                        return '<span class="totalPriceText">-' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                      }else{
                        return "";
                      };
                    }
                    },
                    {"data" : "currency", className:"double-clickable ps-1 pe-1"},
                    {"data" : "exchangeRate", className:"double-clickable ps-1 pe-1", "visible": false},
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.amount * row.exchangeRate).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "type", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "companyId", className:"double-clickable ps-1 pe-1", "visible":false},
];

    table.DataTable({
      order : order,
      "serverSide" : serverSide,
      "processing" : true,
      "autoWidth": true,
      select: {
        style: 'multi',
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
      language: {
        search: '',
        searchPlaceholder: "Search..."
        //processing: '<i class="fa fa-circle-notch fa-spin fa-3x fa-fw" style="z-index:99999;"></i>'
      },
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
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        //console.log(api.page());
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        };
        
      },
      "ajax" : apiSource,
      "columns" : columns
    });

    //sütun gizleme
    table.DataTable().column(2).visible(false);

    //new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        
        //tablo oluştuğunda loading spinner'ını kapatır
        $("#tabPane-" + ef).busyLoad("hide", {
          animation: "fade"
        });

        //sıra numaralarını ekler
        let pageLength = table.DataTable().page.len();
        let page = table.DataTable().page();
        let i = 1 + (page * pageLength);
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });

    });

    table.on('click', 'tbody tr', function (cell) {

      //console.log(table.DataTable().cells(null,1));
   
      //console.log(tableClass.row(idx).data())
  });  

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
        let data = table.DataTable().row(this).data();
  
    /**/htmx.ajax('GET', '/account/soa_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
        window.history.pushState({}, '', addDataHxGet);
    });

    //select all işlemi event'i
    $('#select-all-' + ef).on( "click", function(e) {
      if ($(this).is( ":checked" )) {
          table.DataTable().rows().select();        
      } else {
          table.DataTable().rows().deselect(); 
      }
    });

    //tablodaki filtre
    // table.DataTable().columns().every( function() {
    //   var that = this;

    //   $('input', this.footer()).on('keyup change', function() {
    //       if (that.search() !== this.value) {
    //           that
    //               .search(this.value)
    //               .draw();
    //       }
    //   });
    // });
    
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

function setSOACustomerListDataTable(){/**/
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

  let tableId = '#table-' + ef + "-soaCustomerList";
  let table = $('#table-' + ef + "-soaCustomerList");
/**/let addDataHxGet = "/card/company_add/";
  let addDataHxTarget = addFormBlockSubID;

  let order = [[3, 'desc']];

  let buttons = [
      {
        // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
        className: "tableTopButtons inTableButtons",
        tag: "img",
        attr: {src:"/static/images/icons/datatable/sync.svg"},
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
      },
      {
        tag: "img",
        attr: {src:"/static/images/icons/datatable/xls.svg",href:"/sale/quotation_all_excel/"}, 
        className: "tableTopButtons inTableButtons",
        action: function ( e, dt, node, config ) {
          //window.location.href = "/sale/quotation_all_excel/";
          //htmx.ajax("GET", "/sale/quotation_all_excel/", {target : "#addUpdateDataDialog-inform"});
          htmx.ajax("GET", "/account/soa_send_invoice_filter_excel/", {target : "#addUpdateDataDialogXl"});
        }
      },
      {
        tag: "img",
        attr: {src:"/static/images/icons/datatable/pdf.svg"}, 
        className: "tableTopButtons inTableButtons",
        action: function ( e, dt, node, config ) {
          //window.location.href = "/sale/quotation_all_excel/";
          //htmx.ajax("GET", "/sale/quotation_all_excel/", {target : "#addUpdateDataDialog-inform"});
          htmx.ajax("GET", "/account/soa_send_invoice_filter_pdf/", {target : "#addUpdateDataDialogXl"});
        }
      }
  ];

  let deleteDataButton = $('.deleteData');
  let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/account/process_delete/";
  let serverSide = true;
/**/let apiSource = '/account/api/send_invoices/type_soa/?format=datatables';
    let columns = [
                    {
                      orderable: false,
                      searchable: false,
                      className: 'select-checkbox ps-1 pe-1',
                      "width": "1%",
                      targets: 0,
                      name: "sendInvoices"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable", "visible": false},
                    {"data" : "customer", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      return '<a hx-get="/account/soa_update/' + row.customerId+ '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                    }
                    },
                    {"data" : "billing", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "sendInvoiceNo", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.group == "order"){
                        return row.projectNo;
                      }else if(row.group == "service"){
                        return row.offerNo;
                      };
                    }
                    },
                    {"data" : "vessel", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "imo", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "sendInvoiceDate", className:"double-clickable ps-1 pe-1"},
                    {"data" : "paymentDate", className:"double-clickable ps-1 pe-1"},
                    {"data" : "totalPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "paidPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="totalPriceText">' + (row.totalPrice - row.paidPrice).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "currency", className:"double-clickable"},
                    {"data" : "exchangeRate", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 4 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.exchangeRate * (row.totalPrice - row.paidPrice)).toLocaleString('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "projectNo", "visible": false},
                    {"data" : "offerNo", "visible": false},
                    {"data" : "customerId", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "group", "visible": false}
    ];

  table.DataTable({
    order : order,
    "serverSide" : serverSide,
    "processing" : true,
    "autoWidth": true,
    select: {
      style: 'multi',
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
    language: {
      search: '',
      searchPlaceholder: "Search..."
      //processing: '<i class="fa fa-circle-notch fa-spin fa-3x fa-fw" style="z-index:99999;"></i>'
    },
    dom : 'Bfrtip',
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
    drawCallback: function() {
      var api = this.api();
      var rowCount = api.rows({page: 'current'}).count();
      //console.log(api.page());
      for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
        $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
      };
      
    },
    "ajax" : apiSource,
    "columns" : columns
  });

  //sütun gizleme
  table.DataTable().column(2).visible(false);

  //new $.fn.dataTable.FixedHeader(table);

  //tablo her yüklendiğinde oluşan eylemler.
  // table.DataTable().ajax.reload(function() {
  //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
  // }, false);
  
  //tablo her çizildiğinde oluşan eylemler
  table.on( 'draw.dt', function () {
      htmx.process(tableId);
      
      //tablo oluştuğunda loading spinner'ını kapatır
      $("#tabPane-" + ef).busyLoad("hide", {
        animation: "fade"
      });

      //sıra numaralarını ekler
      let pageLength = table.DataTable().page.len();
      let page = table.DataTable().page();
      let i = 1 + (page * pageLength);
      table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

  });

  table.on('click', 'tbody tr', function (cell) {

    //console.log(table.DataTable().cells(null,1));
 
    //console.log(tableClass.row(idx).data())
});  

  //çift tıklama ile detay sayfalarına gider
  table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/account/soa_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', addDataHxGet);
  });

  //select all işlemi event'i
  $('#select-all-' + ef).on( "click", function(e) {
    if ($(this).is( ":checked" )) {
        table.DataTable().rows().select();        
    } else {
        table.DataTable().rows().deselect(); 
    }
  });

  //tablodaki filtre
  // table.DataTable().columns().every( function() {
  //   var that = this;

  //   $('input', this.footer()).on('keyup change', function() {
  //       if (that.search() !== this.value) {
  //           that
  //               .search(this.value)
  //               .draw();
  //       }
  //   });
  // });
  
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

  // default loading spinner'ı gizler
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});

};

function setSOASupplierListDataTable(){/**/
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

  let tableId = '#table-' + ef + "-soaSupplierList";
  let table = $('#table-' + ef + "-soaSupplierList");
/**/let addDataHxGet = "/card/company_add/";
  let addDataHxTarget = addFormBlockSubID;

  let order = [[3, 'desc']];

  let buttons = [
      {
        // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
        className: "tableTopButtons inTableButtons",
        tag: "img",
        attr: {src:"/static/images/icons/datatable/sync.svg"},
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
      },
      {
        tag: "img",
        attr: {src:"/static/images/icons/datatable/xls.svg",href:"/sale/quotation_all_excel/"}, 
        className: "tableTopButtons inTableButtons",
        action: function ( e, dt, node, config ) {
          //window.location.href = "/sale/quotation_all_excel/";
          //htmx.ajax("GET", "/sale/quotation_all_excel/", {target : "#addUpdateDataDialog-inform"});
          htmx.ajax("GET", "/account/soa_incoming_invoice_filter_excel/", {target : "#addUpdateDataDialogXl"});
        }
      },
      {
        tag: "img",
        attr: {src:"/static/images/icons/datatable/pdf.svg"}, 
        className: "tableTopButtons inTableButtons",
        action: function ( e, dt, node, config ) {
          //window.location.href = "/sale/quotation_all_excel/";
          //htmx.ajax("GET", "/sale/quotation_all_excel/", {target : "#addUpdateDataDialog-inform"});
          htmx.ajax("GET", "/account/soa_incoming_invoice_filter_pdf/", {target : "#addUpdateDataDialogXl"});
        }
      }
  ];

  let deleteDataButton = $('.deleteData');
  let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/account/process_delete/";
  let serverSide = true;
/**/let apiSource = '/account/api/incoming_invoices/type_soa/?format=datatables';
    let columns = [
                    {
                      orderable: false,
                      searchable: false,
                      className: 'select-checkbox ps-1 pe-1',
                      "width": "1%",
                      targets: 0,
                      name: "sendInvoices"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable", "visible": false},
                    {"data" : "seller", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      return '<a hx-get="/account/soa_update/' + row.sellerId+ '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                    }
                    },
                    {"data" : "purchaseOrderNo", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "incomingInvoiceNo", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.group == "order"){
                        return row.projectNo;
                      }else if(row.group == "service"){
                        return row.offerNo;
                      };
                    }
                    },
                    {"data" : "incomingInvoiceDate", className:"double-clickable ps-1 pe-1"},
                    {"data" : "paymentDate", className:"double-clickable ps-1 pe-1"},
                    {"data" : "totalPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "paidPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="totalPriceText">' + (row.totalPrice - row.paidPrice).toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "currency", className:"double-clickable"},
                    {"data" : "exchangeRate", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 4 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.exchangeRate * (row.totalPrice - row.paidPrice)).toLocaleString('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "projectNo", "visible": false},
                    {"data" : "purchasingProject", "visible": false},
                    {"data" : "sellerId", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "group", "visible": false}
    ];

  table.DataTable({
    order : order,
    "serverSide" : serverSide,
    "processing" : true,
    "autoWidth": true,
    select: {
      style: 'multi',
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
    language: {
      search: '',
      searchPlaceholder: "Search..."
      //processing: '<i class="fa fa-circle-notch fa-spin fa-3x fa-fw" style="z-index:99999;"></i>'
    },
    dom : 'Bfrtip',
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
    drawCallback: function() {
      var api = this.api();
      var rowCount = api.rows({page: 'current'}).count();
      //console.log(api.page());
      for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
        $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
      };
      
    },
    "ajax" : apiSource,
    "columns" : columns
  });

  //sütun gizleme
  table.DataTable().column(2).visible(false);

  //new $.fn.dataTable.FixedHeader(table);

  //tablo her yüklendiğinde oluşan eylemler.
  // table.DataTable().ajax.reload(function() {
  //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
  // }, false);
  
  //tablo her çizildiğinde oluşan eylemler
  table.on( 'draw.dt', function () {
      htmx.process(tableId);
      
      //tablo oluştuğunda loading spinner'ını kapatır
      $("#tabPane-" + ef).busyLoad("hide", {
        animation: "fade"
      });

      //sıra numaralarını ekler
      let pageLength = table.DataTable().page.len();
      let page = table.DataTable().page();
      let i = 1 + (page * pageLength);
      table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

  });

  table.on('click', 'tbody tr', function (cell) {

    //console.log(table.DataTable().cells(null,1));
 
    //console.log(tableClass.row(idx).data())
});  

  //çift tıklama ile detay sayfalarına gider
  table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/account/soa_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', addDataHxGet);
  });

  //select all işlemi event'i
  $('#select-all-' + ef).on( "click", function(e) {
    if ($(this).is( ":checked" )) {
        table.DataTable().rows().select();        
    } else {
        table.DataTable().rows().deselect(); 
    }
  });

  //tablodaki filtre
  // table.DataTable().columns().every( function() {
  //   var that = this;

  //   $('input', this.footer()).on('keyup change', function() {
  //       if (that.search() !== this.value) {
  //           that
  //               .search(this.value)
  //               .draw();
  //       }
  //   });
  // });
  
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

  // default loading spinner'ı gizler
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});

};

function setSOANavTabSub(){
  let eSub = elementTag + "-" + elementTagId;

  var efSub = elementTag;
  let uSub = pageUrl;
  //console.log($("#tabNavSub-" + efSub))
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
      console.log(navTagSub.prev());
      navTagSub.prev().children("a").addClass("active");
      tabPaneSub.prev().addClass("show active");
      
      navTagSub.prev().children("a").children("button").show();
      $("#table-" + efSub + "-table").DataTable().columns.adjust();
      $("#table-" + efSub + "-soaFullHistory").DataTable().columns.adjust();
      
      navTagSub.remove();
      tabPaneSub.remove();

      sideBarButtonSub.attr("hx-swap", "afterbegin");
        
    });

    navTagLinkSub.on("shown.bs.tab", function(e){
      $(e.target).children("button").show();
      
      $(e.relatedTarget).children("button").hide();

      $("#table-" + efSub + "-table").DataTable().columns.adjust();
      $("#table-" + efSub + "-soaFullHistory").DataTable().columns.adjust();

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

    //console.log(removeNavSub);
    removeNavSub.click(function(){
      console.log(tabPaneSub.prev());
      navTagSub.prev().children("a").addClass("active");
      tabPaneSub.prev().addClass("show active");
      
      navTagSub.prev().children("a").children("button").show();
      $("#table-" + efSub + "-table").DataTable().columns.adjust();
      $("#table-" + efSub + "-soaFullHistory").DataTable().columns.adjust();
      
      navTagSub.remove();
      tabPaneSub.remove();

      sideBarButtonSub.attr("hx-swap", "afterbegin");
        
    });

    navTagLinkSub.on("shown.bs.tab", function(e){
        $(e.target).children("button").show();
        
        $(e.relatedTarget).children("button").hide();

        $("#table-" + efSub + "-table").DataTable().columns.adjust();
        $("#table-" + efSub + "-soaFullHistory").DataTable().columns.adjust();

        $("#table-" + eSub).DataTable().columns.adjust();

        history.pushState({}, null, uSub);
    });

    navTagSub.css({"display" : "block"});

    // document.querySelectorAll('.form-outline').forEach((formOutline) => {
    //   new mdb.Input(formOutline).update();
    // });
    
  };
};

$(document).ready(function () {
/**/setSOADataTable();
    setSOAFullHistoryDataTable();
    setSOACustomerListDataTable();
    setSOASupplierListDataTable();
    setNavTab();
    setSOANavTabSub();
    setHTMX();

  // Hedeflenen tab'ın ID'sini ve hedeflenen konumu alın
  function moveTabNav(tabId, targetIndex) {
    var tabNav = document.getElementById('tabNavSub-' + elementTag + ''); // <ul> öğesi
    var tabToMove = document.getElementById(tabId); // Hedeflenen tab'ı bul

    if (tabNav && tabToMove) {
        var tabs = tabNav.querySelectorAll('.nav-item'); // Tüm tab'ları seç
        var targetTab = tabs[targetIndex]; // Hedeflenen konumdaki tab'ı bul

        if (targetTab) {
            tabNav.insertBefore(tabToMove, targetTab); // Tab'ı hedeflenen konuma taşı
        }
    }
  };

  moveTabNav('navTag-' + elementTag + '-table', 0);
  moveTabNav('navTag-' + elementTag + '-soaFullHistory', 1);
  moveTabNav('navTag-' + elementTag + '-soaCustomerList', 2);
  moveTabNav('navTag-' + elementTag + '-soaSupplierList', 3);
  //moveTabNav('navTag-' + elementTag + '-soaCustomerList', 2);

  function moveTabPane(tabId, targetIndex) {
    var tabToMove = document.getElementById(tabId); // Hedeflenen tab'ı bul

    if (tabToMove) {
        var parent = tabToMove.parentNode; // Tab'ın ebeveynini al

        if (parent) {
            var tabs = parent.children; // Ebeveynin tüm çocuklarını al (diğer tab'lar)
            var targetTab = tabs[targetIndex]; // Hedeflenen konumdaki tab'ı bul

            if (targetTab) {
                parent.insertBefore(tabToMove, targetTab); // Tab'ı hedeflenen konuma taşı
            }
        }
    }
  }

  

  moveTabPane('tabPane-' + elementTag + '-table', 0);
  // moveTabPane('tabPane-' + elementTag + '-soaFullHistory', 1);
  // moveTabPane('tabPane-' + elementTag + '-soaCustomerList', 2);
  // moveTabPane('tabPane-' + elementTag + '-soaSupplierList', 3);

});





                    
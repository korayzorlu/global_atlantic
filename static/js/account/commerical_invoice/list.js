
function setCommericalInvoiceDataTable(){/**/
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

    let addFormBlockID = "#addFormBlock-sub-" + ef;
    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);
/**/let addDataHxGet = "/account/commerical_invoice_add_manual/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[6, 'desc']];
  
    let buttons = [
        // {
        //   // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/add-file.svg"},
        //   className: "tableTopButtons inTableButtons",
        //   action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, {target : addDataHxTarget, swap : "afterbegin", "push-url" : "true"});
        //     window.history.pushState({}, '', addDataHxGet);
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
            table.DataTable().columns.adjust().draw();
            
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
/**/let deleteDataUrl = "/account/commerical_invoice_delete/";
    let serverSide = true;
/**/let apiSource = '/account/api/commerical_invoices?format=datatables';
/**/let columns = [
                      {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        "width": "1%",
                        targets: 0,
                        name: "commericalInvoices"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable", "visible": false},
                    {"data" : "seller", className:"double-clickable ps-1 pe-1"},
                    {"data" : "customer", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      return '<a hx-get="/account/commerical_invoice_update/' + row.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                      
                    }
                    },
                    {"data" : "commericalInvoiceNo", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "commericalInvoiceDate", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "paymentDate", className:"double-clickable ps-1 pe-1"},
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "transport", className:"double-clickable ps-1 pe-1"},
                    {"data" : "netPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "discountPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="discountPriceText">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "vatPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "totalPrice", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="totalPriceText">' + data.toLocaleString('tr-TR', { currency: row.currency, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "currency", className:"double-clickable"},
                    {"data" : "exchangeRate", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + data.toLocaleString('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 4 }) + '</span>';
                    }
                    },
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.exchangeRate * row.totalPrice).toLocaleString('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 2 }) + '</span>';
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
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
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

    //tablo'da search yapıldığında oluşan eylemler
    table.on( 'search.dt', function () {
      console.log("arandı");
    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
        let data = table.DataTable().row(this).data();

        /**/htmx.ajax('GET', '/account/commerical_invoice_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
        window.history.pushState({}, '', '/account/commerical_invoice_update/' + data["id"] + '/');
    
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
            let typeList = []
            for(let i = 0; i < table.DataTable().rows({selected:true}).data().length; i++){
                idList.push(table.DataTable().rows({selected:true}).data()[i]["id"]);
                //typeList.push(table.DataTable().rows({selected:true}).data()[i]["type"]);
            };
            htmx.ajax("GET", deleteDataUrl + idList, "#addUpdateDataDialog");
            
            table.DataTable().ajax.reload(function() {
              htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
            }, false);
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




$(document).ready(function () {
/**/setCommericalInvoiceDataTable();
    setNavTab();
    setNavTabSub();
    setHTMX();

});







function setSOADetailDatatable(){
    let es = elementTagSub + "-" + elementTagId;
    let ef = elementTag;
    let ei = elementTagId;

    //tablo oluşurken loading spinner'ını açar
    $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("show", {
        animation: false,
        spinner: "pulsar",
        maxSize: "150px",
        minSize: "150px",
        text: "Loading ...",
        background: "rgba(69, 83, 89, 0.6)",
        color: "#455359",
        textColor: "#fff"
    });

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/sale/inquiry_part_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    

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
        {
          extend: "excelHtml5",
          // text: '<i class="fa-solid fa-file-excel" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to excel file"></i>',
          className: "tableTopButtons inTableButtons",
          tag: "img",
          attr: {src:"/static/images/icons/datatable/xls.svg"},
          title: 'Company report with vessels',
          exportOptions: {
            format: {
                body: function(data, row, column, node) {
                    console.log("column: " + column + "data: " + data + "type: " + typeof data);
                    // Sadece veri hücrelerinin değerini döndür
                    if(column == 4){
                      var newData = data.replace(".", "").replace(",", ".").replace(/<[^>]+>/g, '');
                      return newData;
                    }else if(column == 5){
                      var newData = data.replace(".", "").replace(",", ".").replace(/<[^>]+>/g, '');
                      return newData;
                    }else if(column == 7){
                      var newData = data.replace(".", "").replace(",", ".").replace(/<[^>]+>/g, '');
                      return newData;
                    }else if(typeof data == "number"){
                      return data;
                    }else{
                      var newData = data.replace(/<[^>]+>/g, '');
                      return newData;
                    };
                    //return data.replace(/<[^>]*>?/gm, '');
                }
            },
            columns: ':visible'
          }
        },
        // {
        //   extend: "pdfHtml5",
        //   // text: '<i class="fa-solid fa-file-pdf" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to pdf file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/pdf.svg"},
        // },
        // {
        //   // text: '<i class="fa-solid fa-print" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Print"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/printer.svg"},
        //   action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', "/account/soa_pdf/" + ei + "/", {target : "#tabContSub-" + ei, swap : "afterbegin", "push-url" : "true"});
        //     window.history.pushState({}, '', "/account/soa_pdf/" + ei + "/");
        //   }
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
        },
        // {
        //   tag: "div",
        //   attr: {}, 
        //   className: "dropdown soaDetailDropdown",
        //   text: `<button class="tableTopButtons inTableButtons dropdown-toggle" type="button" data-mdb-dropdown-init aria-expanded="false" name="pdfButton">
        //           <img src="/static/images/icons/flaticon/{{user.profile.theme}}/setting.svg" alt="" style="height: 18px;">
        //         </button>
        //         <ul class="dropdown-menu">
        //           <li>
        //             <a class="dropdown-item" hx-get="/account/soa_pdf/` + ei + `" hx-target="#tabContSub-` + ei + ` hx-swap="afterbegin" hx-push-url="true" style="cursor:pointer;">Debt Pdf</a>
        //           </li>
        //         </ul>`,
        //   action: function ( e, dt, node, config ) {""
        //   }
        // },
        {
          tag: "button",
          attr: {type:"button"}, 
          className: "btn btn-danger bg-blue-esms text-white ms-auto",
          text: "Debt Pdf",
          action: function ( e, dt, node, config ) {
            htmx.ajax('GET', "/account/soa_pdf/" + ei + "/", {target : "#tabContSub-" + ei, swap : "afterbegin", "push-url" : "true"});
            window.history.pushState({}, '', "/account/soa_pdf/" + ei + "/");
          }
        },
        {
          tag: "button",
          attr: {type:"button"}, 
          className: "btn btn-danger bg-blue-esms text-white ms-auto",
          text: "Credit Pdf",
          action: function ( e, dt, node, config ) {
            htmx.ajax('GET', "/account/soa_incoming_pdf/" + ei + "/", {target : "#tabContSub-" + ei, swap : "afterbegin", "push-url" : "true"});
            window.history.pushState({}, '', "/account/soa_incoming_pdf/" + ei + "/");
          }
        },
    ];
    
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/account/soa_delete/";
    let serverSide = true;
/**/let apiSource = '/account/api/soa_multiple?customer=' + soaId + '&format=datatables';
/**/let columns = [ 
                    {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%",
                        "visible": false
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable ps-1 pe-1"},
                    {"data" : "date", className:"double-clickable ps-1 pe-1"},
                    {"data" : "type", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      if(data == "IncomingInvoice"){
                        return "INCOMING INVOICE"
                      }else if(data == "SendInvoice"){
                        return "SEND INVOICE"
                      }else if(data == "Payment"){
                        if(row.paymentType == "in"){
                          return "PAYMENT IN"
                        }else if(row.paymentType == "out"){
                          return "PAYMENT OUT"
                        };
                      };
                    }
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "IncomingInvoice"){
                        if(row.projec){
                          return row.project.projectNo;
                        }else{
                          return "";
                        };
                      }else if(row.type == "SendInvoice"){
                        if(row.group == "order"){
                          return row.project.projectNo;
                        }else if(row.group == "service"){
                          return row.offer.offerNo;
                        }else{
                          return '';
                        };
                      }else if(row.type == "Payment"){
                        if(row.paymentType == "in"){
                          return '';
                        }else if(row.paymentType == "out"){
                          return '';
                        };
                      };
                    }
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "IncomingInvoice"){
                        return row.incomingInvoiceNo;
                      }else if(row.type == "SendInvoice"){
                        return row.sendInvoiceNo;
                      }else if(row.type == "Payment"){
                        if(row.paymentType == "in"){
                          return '';
                        }else if(row.paymentType == "out"){
                          return '';
                        };
                      };
                    }
                    },
                    {"data" : "price", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "IncomingInvoice"){
                        return '<span class="totalPriceText">-' + data.toLocaleString('tr-TR', { currency: row.currency.code, minimumFractionDigits: 2 }) + '</span>';
                      }else if(row.type == "SendInvoice"){
                        return '<span class="totalPriceText">' + data.toLocaleString('tr-TR', { currency: row.currency.code, minimumFractionDigits: 2 }) + '</span>';
                      }else if(row.type == "Payment"){
                        if(row.paymentType == "in"){
                          return '';
                        }else if(row.paymentType == "out"){
                          return '';
                        };
                      };
                    }
                    },
                    {"data" : "price", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      if(row.type == "IncomingInvoice"){
                        return '';
                      }else if(row.type == "SendInvoice"){
                        return '';
                      }else if(row.type == "Payment"){
                        if(row.paymentType == "in"){
                          return '<span class="totalPriceText">' + data.toLocaleString('tr-TR', { currency: row.currency.code, minimumFractionDigits: 2 }) + '</span>';
                        }else if(row.paymentType == "out"){
                          return '<span class="totalPriceText">-' + data.toLocaleString('tr-TR', { currency: row.currency.code, minimumFractionDigits: 2 }) + '</span>';
                        };
                      };
                    }
                    },
                    {"data" : "currency.code", className:"double-clickable ps-1 pe-1"},
                    {"data" : "currency.symbol", className:"double-clickable ps-1 pe-1", "visible": false},
                    {"data" : "", className:"double-clickable text-end ps-1 pe-1", render: function (data, type, row, meta){
                      return '<span class="">' + (row.price * row.currency.forexBuying).toLocaleString('tr-TR', { currency: row.currency.code, minimumFractionDigits: 2 }) + '</span>';
                    }
                    },
                    {"data" : "customer", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "paymentType", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "group", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "project.projectNo", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "offer.offerNo", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "sendInvoiceNo", className:"double-clickable ps-1 pe-1", "visible":false},
                    {"data" : "incomingInvoiceNo", className:"double-clickable ps-1 pe-1", "visible":false}
];

    //$.fn.dataTable.moment('DD.MM.YYYY HH:mm');

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
      //paging : false,
      scrollY : "74vh",
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
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        console.log(rowCount)
        //console.log(api.page());
        // if(api.rows().data()[0]){
        //   let customerName = api.rows().data()[0]["customer"]["name"];
        //   $(tableId + ' tbody').prepend($("<tr ><td class='text-center fw-bold text-white' colspan='9' style='background-color:#9d2235;'>" + customerName +"</td></tr>"));
        // }else{
        //   $(tableId + ' tbody').prepend($("<tr ><td class='text-center fw-bold text-white' colspan='9' style='background-color:#9d2235;'>" + soaName +"</td></tr>"));
        // };
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        };
        
      },
      "ajax" : apiSource,
      "columns" : columns
    });

    //sütun gizleme
    table.DataTable().column(2).visible(false);

    
    
    //new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    }, false);
    
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

    $(".soaDetailDropdown").removeClass("dt-button");
    $(".soaDetailDropdown").css({"display":"inline-block"});
    

};

function setSOADetailNavTabSub(){
  let eSub = elementTag + "-" + elementTagId;

  var efSub = elementTag;
  let uSub = pageUrl;
  console.log($("#tabNavSub-" + efSub))
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

    console.log(removeNavSub);
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
    /**/setSOADetailDatatable();
        setSOADetailNavTabSub();
        setHTMX();
    
    });
    

function setOrderInProcessADataTable(){/**/
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
/**/let addDataHxGet = "/sale/quotation_add/";
    let addDataHxTarget = addFormBlockID;

    let order = [[5, 'desc']];
  
    let buttons = [
        // {
        //   text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        //   }
        // },
        // {
        //   text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
        //   className: "deleteData tableTopButtons inTableButtons delete-" + ef + ""
        // },
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

    //////////////////Tabloya Özel/////////////////
    
    function format(d) {
      // `d` is the original data object for the row

      if(d.type == "Order"){

        if(d.vessel){
          var vessel = d.vessel;
        }else{
          var vessel = "";
        };
  
        if(d.agent){
          var agent = d.agent.name;
        }else{
          var agent = "";
        };
  
        if(d.maker){
          var maker = d.maker;
        }else{
          var maker = "";
        };
  
        if(d.makerType){
          var makerType = d.makerType;
        }else{
          var makerType = "";
        };
  
        var poList = []
  
        for(var i = 0; i < d.purchaseOrders.length; i++){
          poList.push(d.purchaseOrders[i].id)
        };

        var poNoList = []
  
        for(var i = 0; i < d.purchaseOrders.length; i++){
            poNoList.push(d.purchaseOrders[i].purchaseOrder)
        };

        if(d.purchaseOrders[0].status == "collecting"){
          var incomingInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-spinner fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Incoming Invoice</button>';
          var sendInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-spinner fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</button>';
          var proformaInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/proforma_invoice_add/oc_' + d.orderConfirmationId + '" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</a>';
        }else{
          var incomingInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/incoming_invoice_bulk_add/type_order_po_' + poList + '" hx-target="#addUpdateDataDialogXl" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Incoming Invoice</a>';
          var sendInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/send_invoice_add/id_' + d.orderConfirmationId + '_type_order" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</a>';
          //var proformaInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</button>';
          var proformaInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/proforma_invoice_add/oc_' + d.orderConfirmationId + '" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</a>';
        };

        if(d.purchaseOrders[0].sendInvoiced){
          //var sendInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-circle-check fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</button>';
          var sendInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/send_invoice_add/id_' + d.orderConfirmationId + '_type_order" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</a>';
          //var proformaInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-circle-check fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</button>';
          var proformaInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/proforma_invoice_add/oc_' + d.orderConfirmationId + '" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</a>';
        };
      if(d.purchaseOrders[0].proformaInvoiced){
        //var proformaInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-circle-check fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</button>';
        var proformaInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/proforma_invoice_add/oc_' + d.orderConfirmationId + '" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Proforma Invoice</a>';
      };
        
        
        
  
        return (
            '<table class="table table-borderless">' +
  
            '<tr>' +
            
              '<td class="fw-bold text-uppercase">Customer <span class="text-right" style="float:right;">:</span></td><td>' + d.company + '</td>' +
              '<td class="fw-bold text-uppercase">Delivery Agent <span class="text-right" style="float:right;">:</span></td><td>' + agent + '</td>' +
              '<td class="fw-bold text-uppercase">Supplier <span class="text-right" style="float:right;">:</span></td><td>' + d.company + '</td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
            
            '</tr>' +
  
            '<tr>' +
            
              '<td class="fw-bold text-uppercase">Vessel <span class="text-right" style="float:right;">:</span></td><td>' + d.vessel + '</td>' +
              '<td class="fw-bold text-uppercase">Port <span class="text-right" style="float:right;">:</span></td><td>' + d.port + '</td>' +
              '<td class="fw-bold">PO List <span class="text-right" style="float:right;">:</span></td><td>' + poNoList + '</td>' +
              '<td></td><td></td>' +
              '<td></td><td>' + incomingInvoiceButton + '</td>' +
            
            '</tr>' +
  
            '<tr>' +
            
              '<td class="fw-bold">Maker <span class="text-right" style="float:right;">:</span></td><td>' + maker+ '</td>' +
              '<td class="fw-bold text-uppercase">Transportation Com. <span class="text-right" style="float:right;">:</span></td><td>' + d.transportationCompany + '</td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
              '<td></td><td>' + sendInvoiceButton + '</td>' +
            
            '</tr>' +
  
            '<tr>' +
            
              '<td class="fw-bold text-uppercase">Type <span class="text-right" style="float:right;">:</span></td><td>' + makerType + '</td>' +
              '<td class="fw-bold text-uppercase">AWB No <span class="text-right" style="float:right;">:</span></td><td>' + d.waybillNo + '</td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
              '<td></td><td>' + proformaInvoiceButton + '</td>' +
            
            '</tr>' +
  
            '<tr>' +
            
              '<td class="fw-bold text-uppercase">OC No <span class="text-right" style="float:right;">:</span></td><td>' + d.orderConfirmation + '</td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
            
            '</tr>' +
  
            '<tr>' +
            
              '<td class="fw-bold text-uppercase">OC Date <span class="text-right" style="float:right;">:</span></td><td>' + d.orderConfirmationDate + '</td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
              '<td></td><td></td>' +
            
            '</tr>' +
  
            '</table>'
        )

      }else if(d.type == "Service"){

        if(d.vessel){
          var vessel = d.vessel;
        }else{
          var vessel = "";
        };

        if(d.status == "Active"){
          var sendInvoiceButton = '<button class="btn btn-dark btn-sm ms-auto w-100 text-start" href="#" disabled><i class="fa-solid fa-spinner fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</button>';
        }else if(d.status == "Invoiced"){
            var sendInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/send_invoice_add/id_' + d.offerId + '_type_service" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</a>';
        }else if(d.status == "Invoicing"){
            var sendInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/send_invoice_add/id_' + d.offerId + '_type_service" hx-target="#addUpdateDataDialog" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Send Invoice</a>';
        };

        return (
          '<table class="table table-borderless">' +

          '<tr>' +
          
            '<td class="fw-bold text-uppercase">Customer <span class="text-right" style="float:right;">:</span></td><td>' + d.company + '</td>' +
            '<td class="fw-bold text-uppercase">Machine Type <span class="text-right" style="float:right;">:</span></td><td>' + d.makerType + '</td>' +
            '<td class="fw-bold text-uppercase">Offer Date <span class="text-right" style="float:right;">:</span></td><td>' + d.projectDate + '</td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td class="fw-bold text-uppercase">Vessel <span class="text-right" style="float:right;">:</span></td><td>' + vessel + '</td>' +
            '<td class="fw-bold text-uppercase">Customer Ref. <span class="text-right" style="float:right;">:</span></td><td>' + "" + '</td>' +
            '<td class="fw-bold">Payment Type<span class="text-right" style="float:right;">:</span></td><td>' + "" + '</td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td class="fw-bold">Equipment <span class="text-right" style="float:right;">:</span></td><td>' + d.equipment + '</td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td>' + sendInvoiceButton + '</td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '</table>'
      )

      }else if(d.type == "Purchasing"){
        var poList = []
        console.log(d.purchaseOrders)
        for(var i = 0; i < d.purchaseOrders.length; i++){
          poList.push(d.purchaseOrders[i].id)
        };

        var poNoList = []
  
        for(var i = 0; i < d.purchaseOrders.length; i++){
            poNoList.push(d.purchaseOrders[i].purchaseOrder)
        };

        var incomingInvoiceButton = '<a class="btn btn-sm ms-auto w-100 text-start bg-red-900 text-white" id="incomingInvoiceButton" hx-get="/account/incoming_invoice_bulk_add/type_purchasing_po_' + poList + '" hx-target="#addUpdateDataDialogXl" hx-push-url="true"><i class="fa-solid fa-hourglass-start fa-xl" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Incoming Invoice"></i> Incoming Invoice</a>';

        return (
          '<table class="table table-borderless">' +

          '<tr>' +
          
            '<td class="fw-bold text-uppercase">PO List <span class="text-right" style="float:right;">:</span></td><td>' + poNoList + '</td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
           '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td>' + incomingInvoiceButton + '</td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '<tr>' +
          
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
            '<td></td><td></td>' +
          
          '</tr>' +

          '</table>'
      )

      };

      
    };
    //////////////////Tabloya Özel-end/////////////////
  
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/sale/quotation_delete/";
    let serverSide = true;
/**/let apiSource = '/account/api/process_statuses?format=datatables';

    let columns = [ 
        {
        orderable: false,
        searchable: false,
        className: 'select-checkbox ps-1 pe-1',
        targets: 0,
        "width": "1%"
        },
        {"data" : "", className:"double-clickable ps-1 pe-1"},
        {"data" : "id", className:"double-clickable ps-1 pe-1"},
        {
                    className: 'dt-control',
                    orderable: false,
                    data: null,
                    defaultContent: ''
        },
        // {"data" : "", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
        //   if(row.type == "OrderTracking"){
        //     return '<a hx-get="/account/order_in_process_update/' + row.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + row.project.projectNo + '</a>';
        //   }else if(row.type == "Offer"){
        //     return '<a hx-get="/account/order_in_process_update/' + row.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + row.offerNo + '</a>';
        //   };
            
        // }
        // },
        {"data" : "projectNo", className:"double-clickable ps-1 pe-1"},
        {"data" : "created_date", className:"double-clickable ps-1 pe-1"},
        {"data" : "company", className:"double-clickable text-start ps-1 pe-1"},
        {"data" : "vessel", className:"double-clickable text-start ps-1 pe-1"},
        {"data" : "items", "width" : "12%", className:"double-clickable text-start shadow-0 ps-1 pe-1", render: function (data, type, row, meta){
        if(data){
            if(data["parts"]["remaining"] > 0){
            return '<div class="alert" role="alert" data-mdb-color="warning" style="padding:2px 5px;margin:0;"><i class="fas fa-exclamation-triangle me-3"></i>' + data["parts"]["remaining"] + ' remaining items</div>'
            }else{
            return '<div class="alert" role="alert" data-mdb-color="success" style="padding:2px 5px;margin:0;"><i class="fas fa-check-circle me-3"></i>All items completed</div>'
            };
        }else{
            return '<div class="alert" role="alert" data-mdb-color="success" style="padding:2px 5px;margin:0;"><i class="fas fa-check-circle me-3"></i>No items data</div>';
        };
        }
        },
        {"data" : "type", className:"double-clickable shadow-0 ps-1 pe-1", render: function (data, type, row, meta){
            if(data == "Order"){
              return '<div class="alert text-start" role="alert" data-mdb-color="primary" style="padding:2px 5px;margin:0;"><i class="fas fa-hand-holding-dollar me-3"></i>' + data + '</div>';
            }else if(data == "Service"){
              return '<div class="alert text-start" role="alert" data-mdb-color="danger" style="padding:2px 5px;margin:0;"><i class="fas fa-screwdriver-wrench me-3"></i>' + data + '</div>';
            }else if(data == "Purchasing"){
              return '<div class="alert text-start" role="alert" data-mdb-color="dark" style="padding:2px 5px;margin:0;"><i class="fas fa-cart-shopping me-3"></i>' + data + '</div>';
            };
          }
        },
        {"data" : "status", className:"double-clickable text-start shadow-0 ps-1 pe-1", render: function (data, type, row, meta){
        if(row.type == "Order"){
            if(data == "Collecting"){
            return '<div class="alert" role="alert" data-mdb-color="secondary" style="padding:2px 5px;margin:0;"><i class="fas fa-hourglass-half me-3"></i>Collecting</div>';
            }else if(data == "Collected"){
            return '<div class="alert" role="alert" data-mdb-color="warning" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-dollar-to-slot me-3"></i>Invoicing</div>';
            }else if(data == "Invoiced"){
            return '<div class="alert" role="alert" data-mdb-color="success" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-check me-3"></i>Invoiced</div>';
            };
        }else if(row.type == "Service"){
            if(data == "Active"){
            return '<div class="alert" role="alert" data-mdb-color="secondary" style="padding:2px 5px;margin:0;"><i class="fas fa-hourglass-half me-3"></i>Active</div>';
            }else if(data == "Invoiced"){
                return '<div class="alert" role="alert" data-mdb-color="success" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-check me-3"></i>Invoiced</div>';
            }else if(data == "Invoicing"){
                return '<div class="alert" role="alert" data-mdb-color="warning" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-dollar-to-slot me-3"></i>Invoicing</div>';
            };
        }else if(row.type == "Purchasing"){
            if(row.invoiced == true){
            return '<div class="alert" role="alert" data-mdb-color="success" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-check me-3"></i>Invoiced</div>';
            }else{
            return '<div class="alert" role="alert" data-mdb-color="warning" style="padding:2px 5px;margin:0;"><i class="fas fa-circle-dollar-to-slot me-3"></i>Invoicing</div>';
            };
        };
        }
        },
        {"data" : "purchaseOrders", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "orderConfirmation", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "orderConfirmationDate", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "orderConfirmationId", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "offerId", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "equipment", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "maker", className:"double-clickable ps-1 pe-1", "visible":false},
        {"data" : "makerType", className:"double-clickable ps-1 pe-1", "visible":false}
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
      "searching": true,
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
        //render: DataTable.render.datetime('DD.MM.YYYY')
      }],
      createdRow: function(row, data, index) {
        var orderInProcessRemaining = data.items;
        if(orderInProcessRemaining){
          if(orderInProcessRemaining["parts"]["remaining"] > 0){
            $('td:eq(7)', row).addClass("tableAlert-warning");
          }else{
            $('td:eq(7)', row).addClass("tableAlert-success");
          };
        }else{
          $('td:eq(7)', row).addClass("tableAlert-success");
        };

        var orderInProcessType = data.type;
        if(orderInProcessType == "Order"){
          $('td:eq(8)', row).addClass("tableAlert-primary");
          var orderInProcessStatus = data.status;
          if(orderInProcessStatus == "Collecting"){
            $('td:eq(9)', row).addClass("tableAlert-secondary");
          }else if(orderInProcessStatus == "Collected"){
            $('td:eq(9)', row).addClass("tableAlert-warning");
          }else if(orderInProcessStatus == "Invoiced"){
            $('td:eq(9)', row).addClass("tableAlert-success");
          };
        }else if(orderInProcessType == "Service"){
          $('td:eq(8)', row).addClass("tableAlert-danger");
          var orderInProcessStatus = data.status;
          if(orderInProcessStatus == "Active"){
            $('td:eq(9)', row).addClass("tableAlert-secondary");
          }else if(orderInProcessStatus == "Invoiced"){
            $('td:eq(9)', row).addClass("tableAlert-success");
          }else if(orderInProcessStatus == "Invoicing"){
            $('td:eq(9)', row).addClass("tableAlert-warning");
          };
        }else if(orderInProcessType == "Purchasing"){
          $('td:eq(8)', row).addClass("tableAlert-dark");
          var orderInProcessStatus = data.status;
          if(orderInProcessStatus == "Invoiced"){
            $('td:eq(9)', row).addClass("tableAlert-success");
          }else if(orderInProcessStatus == "Invoicing"){
            $('td:eq(9)', row).addClass("tableAlert-warning");
          };
        };

        
      },
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        }
      },
      "ajax" : apiSource,
      "columns" : columns
    });
    
    $.fn.dataTable.moment('DD.MM.YYYY');

    //////////////////Tabloya Özel/////////////////
    // Add event listener for opening and closing details
    //+ butonu ile tablo üzerinde özet detaylar görüntüler
    table.on('click', 'td.dt-control', function (e) {
      let tr = e.target.closest('tr');
      let row = table.DataTable().row(tr);

      if (row.child.isShown()) {
          // This row is already open - close it
          row.child.hide();
      }
      else {
          // Open this row
          console.log(format(row.data()));
          row.child(format(row.data())).show();
      };
      htmx.process(tableId);
    });
   
    //////////////////Tabloya Özel-end/////////////////

    //sütun gizleme
    table.DataTable().column(2).visible(false);
    //table.DataTable().column(9).visible(false);
    //table.DataTable().column(11).visible(false);
  
    new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    //     /////////////tabloya Özel/////////////
    //     //MDB Alert'lerin çalışması için
    //     var alerts = document.querySelectorAll(".alert");
    //         for (var i = 0; i < alerts.length; i++) {
    //           var alert = alerts[i];
    //           new mdb.Alert(alert);
    //     };
    //     /////////////tabloya Özel-end/////////////
    // }, false);
    
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
  
    /**/htmx.ajax('GET', '/account/order_in_process_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
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

    

};




$(document).ready(function () {
/**/setOrderInProcessADataTable();
    setNavTab();
    setNavTabSub();
    setHTMX();

});







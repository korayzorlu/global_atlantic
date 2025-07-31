function setQuotationPartDetaiOCDatatable(){
    let es = elementTagSub + "-" + elementTagId;

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
/**/let addDataHxGet = "/sale/quotation_part_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    

    let order = [[1, 'asc']];

    let buttons = [
        // {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        // className: "tableTopButtons inTableButtons",
        // action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        // }
        // },
        // {
        //     text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
        //     className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        // },
        {
            // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
            tag: "img",
            attr: {src:"/static/images/icons/datatable/sync.svg"},
            className: "tableTopButtons inTableButtons",
            action: function ( e, dt, node, config ) {
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

                table.DataTable().ajax.reload()

                table.on( 'draw.dt', function () {
                    htmx.process(tableId);
                    $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                      animation: "fade"
                    });
                });
            }
        }
    ];

    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/sale/quotation_part_delete/";
    let serverSide = false;
/**/let apiSource = '/sale/api/quotation_parts?quotation=' + quotationId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "sequency","width": "3%",className:"ps-1 pe-1","visible":false},
        {"data" : "alternative","width": "1%", className:"reorder ps-1 pe-1", render: function (data, type, row, meta){
            if(data == true){
              return row.sequency + "-A"
            }else{
              return row.sequency
            };
            
          }
          },
        {"data" : "id", "visible" : false},
        {"data" : "partNo", className:"ps-1 pe-1 text-start"},
        {"data" : "description", className:"ps-1 pe-1 text-start"},
        {"data" : "supplier", className:"ps-1 pe-1 text-start"},
        {"data" : "quantity", className:"ps-1 pe-1 text-end"},
        {"data" : "unit", className:"ps-1 pe-1"},
        {"data" : "unitPrice1", className:"ps-1 pe-1 text-end", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice1", className:"ps-1 pe-1 text-end", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "profit", className:"ps-1 pe-1 text-end"},
        {"data" : "unitPrice2", className:"ps-1 pe-1 text-end", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice2", className:"ps-1 pe-1 text-end", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "discount", className:"ps-1 pe-1 text-end"},
        {"data" : "unitPrice3", className:"ps-1 pe-1 text-end", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice3", className:"ps-1 pe-1 text-end", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "availabilityChar", className:"ps-1 pe-1"},
        {"data" : "availabilityType", className:"ps-1 pe-1"},
        {"data" : "currency", className:"ps-1 pe-1", "visible" : false}
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
        //"pageLength": 20,
        paging : false,
        scrollY : "38vh",
        scrollX : true,
        scrollCollapse: true,
        // rowReorder: {
        //   dataSrc: 'sequency',
        //   editor: editor,
        //   selector: 'td:nth-child(2)'
        // },
        rowReorder : false,
        fixedHeader: {
          header: true,
          headerOffset: $('#fixed').height()
        },
        responsive : false,
        language: { search: '', searchPlaceholder: "Search..." },
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
        createdRow: function(row, data, index) {

            var alternative = data.alternative;
  
            if(alternative == true){
              $('td:eq(1)', row).removeClass("reorder")
            };
          },
        drawCallback: function() {
            var api = this.api();
            var rowCount = api.rows({page: 'current'}).count();
            
            for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
              $(tableId + ' tbody').append($("<tr ></tr>"));
            }
        },
        "ajax" : apiSource,
        "columns" : columns
      });

    //new $.fn.dataTable.FixedHeader( table );
    
    //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId);
    // }, false);

    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
        });
    });


   
    
    //veri silme butonu
    if(deleteDataButton){
        $(deleteDataButtonId).click(function (){
            console.log(table.DataTable().row({selected:true}).data()["id"]);
            //htmx.ajax("GET", deleteDataUrl + table.DataTable().row({selected:true}).data()["id"], "#addUpdateDataDialog");

            let idList = []
            for(let i = 0; i < table.DataTable().rows({selected:true}).data().length; i++){
                idList.push(table.DataTable().rows({selected:true}).data()[i]["id"]);
            };

            htmx.ajax("POST", deleteDataUrl + idList, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
            setTimeout(function(){
                table.DataTable().ajax.reload(function() {
                    htmx.process(tableId);
                }, false);
            },500);
            
            console.log(idList);
        });
    };

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});





    
};

function setNavTabSubOrderConfirmation(){
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

function formSubmitMessageOrderConfirmation(){
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
  
    
};

function setHTMXOrderConfirmation(){
    let ee = elementTag;
    let ei = elementTagId;
    let es = elementTagSub + "-" + elementTagId;
  
    let tableBox = $(".tableBox-" + ee);
    let tableId = "#table-" + ee;
    let table = $("#table-" + ee);
  
    let modalId = "#addUpdateDataModal-" + ee + "-" + ei;
    let dialogId = "addUpdateDataDialog-" + ee + "-" + ei;

    let modalIdp = "#addUpdateDataModal-" + ee + "-" + ei + "-proforma";
    let dialogIdp = "addUpdateDataDialog-" + ee + "-" + ei + "-proforma";
  
    //htmx dialog gösterme
    let modal = new bootstrap.Modal($(modalId));
    let modalp = new bootstrap.Modal($(modalIdp));
  
    //open
    htmx.on("htmx:afterSwap", (e) => {
        if (e.detail.target.id == dialogId) {
          console.log(location.href);
          modal.show();
        };
        if (e.detail.target.id == dialogIdp) {
            console.log(location.href);
            modalp.show();
          };
        if(e.detail.target.id == "tabContSub-" + ee){
            $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("show", {
                animation: false,
                spinner: "pulsar",
                maxSize: "150px",
                minSize: "150px",
                text: "Loading ...",
                background: "rgba(69, 83, 89, 0.6)",
                color: "#455359",
                textColor: "#fff"
            });
            $(tableId).DataTable().ajax.reload(function(){
                htmx.process(tableId);
            },false);
            table.on( 'draw.dt', function () {
                htmx.process(tableId);
                $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
                    animation: "fade"
                });
            });
        };
        if(e.detail.target.id == "addFormBlock-inform-d-justDetail-" + es){
            $("#table-" + es).DataTable().ajax.reload(function(){
                htmx.process("#table-" + es);
            },false);
            
        };
    });
    //submitted
    htmx.on("htmx:beforeSwap", (e) => {
        if (e.detail.target.id == dialogId && !e.detail.xhr.response) {
          console.log(e.detail.xhr.status);
          modal.hide();
          e.detail.shouldSwap = false
        };
        if (e.detail.target.id == dialogIdp && !e.detail.xhr.response) {
            console.log(e.detail.xhr.status);
            modalp.hide();
            e.detail.shouldSwap = false
          };
        if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
                e.detail.shouldSwap = false;
            $(tableId).DataTable().ajax.reload(function(){
                htmx.process(tableId);
            },false);
        };
        if (e.detail.target.id == "addFormBlock-inform-d-justDetail-" + es && !e.detail.xhr.response) {
            e.detail.shouldSwap = false;
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
            $("#table-" + es).DataTable().ajax.reload(function(){
                htmx.process("#table-" + es);
            },false);
            $("#table-" + es).DataTable().on( 'draw.dt', function () {
                htmx.process("#table-" + es);
                $("body").busyLoad("hide", {
                    animation: "fade"
                });
            });
            history.pushState({}, null, detailRefererPathSub);
          };
    });
    //cancelled
    htmx.on("hidden.bs.modal", (e) => {
        if (e.target.id == dialogId) {
          console.log(location.href);
          document.getElementById(dialogId).innerHTML = "";
        };
        if (e.target.id == dialogIdp) {
            console.log(location.href);
            document.getElementById(dialogIdp).innerHTML = "";
          };
        if (e.target.id == "addFormBlock-inform-d-justDetail-" + es) {
            document.getElementById("addFormBlock-inform-d-justDetail-" + es).innerHTML = "";
        };
    });
  
  };

$(document).ready(function () {
    setQuotationPartDetaiOCDatatable();
    //setHTMXOrderConfirmation();
    setNavTabSubOrderConfirmation();
    formSubmitMessageOrderConfirmation();
    
});
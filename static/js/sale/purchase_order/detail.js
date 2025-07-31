function setPurchaseOrderPartDetailDatatable(){
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
/**/let addDataHxGet = "/sale/quotation_part_update/" + elementTagId + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    

    let order = [[1, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/sale/api/purchase_order_parts/editor/",
        table: tableId,
        idSrc: "id",
        fields: [
            {
                label: "note",
                name: "note",
            },
            {
                label: "remark",
                name: "remark",
                type: "textarea"
            },
        ]
    });
    //////////////////Tabloya Özel-end/////////////////

    let buttons = [
        // {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        // className: "tableTopButtons inTableButtons",
        // action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        // }
        // },
        // {
        //     // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
        //     tag: "img",
        //     attr: {src:"/static/images/icons/datatable/deletefile.svg"},
        //     className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        // },
        {
            // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
            tag: "img",
            attr: {src:"/static/images/icons/datatable/sync.svg"},
            className: "tableTopButtons inTableButtons",
            action: function ( e, dt, node, config ) {
                $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("show", {
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
                    $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("hide", {
                      animation: "fade"
                    });
                });
            }
        }
    ];

    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/sale/purchase_order_part_delete/";
    let serverSide = false;
/**/let apiSource = '/sale/api/purchase_order_parts?purchaseOrder=' + purchaseOrderId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "sequency",className: "editable", "width": "1%"},
        {"data" : "id", "visible" : false},
        {"data" : "partNo", className:"text-start ps-1 pe-1", "width": "15%"},
        {"data" : "description", className:"text-start ps-1 pe-1", "width": "25%"},
        {"data" : "quantity", className:"text-end ps-1 pe-1", "width": "5%"},
        {"data" : "unit", className:"ps-1 pe-1", "width": "1%"},
        {"data" : "unitPrice", className:"text-end ps-1 pe-1", "width": "8%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice", className:"text-end ps-1 pe-1", "width": "8%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "availability", className:"text-end ps-1 pe-1",  orderable: false, "width": "8%", render: function (data, type, row, meta){
            if(data > 1){
            return data + " days";
            }else if(data == 1){
            return data + " day";
            }else if(data < 1){
            return data + " day";
            }else{
            return data + " day";
            };
        }
        },
        {"data" : "note", className:"editable note ps-1 pe-1", orderable: false, "width": "13%"},
        {"data" : "remark", className:"editable remark ps-1 pe-1", orderable: false, "width": "15%"},
        {"data" : "currency", "visible" : false}
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
        scrollY : "30vh",
        scrollX : true,
        scrollCollapse: true,
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

    new $.fn.dataTable.FixedHeader(table);
    
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

    //////////////////Tabloya Özel/////////////////
    //Tıklanan hücrede edit yapılmasını sağlar.
    table.DataTable().on( 'click', 'tbody td.editable', function (e) {
        editor.inline(this, {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });

        let thisColumn = table.DataTable().cell(this).index().column;
        editor.on('submitSuccess', function (e, json, data) {
            if(thisColumn == 1){
              $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("show", {
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
                  $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("hide", {
                    animation: "fade"
                  });
              });
            };
        });
    });

    //remark area
    editor.on('open', function (e, json, data, mode, action) {
        $("#DTE_Field_remark").parent().parent().parent().parent().parent().parent().css({"width":"30%"});
        table.DataTable().columns.adjust();
    });

    editor.on('preClose', function (e, json, data) {
        $("#DTE_Field_remark").parent().parent().parent().parent().parent().parent().css({"width":"10%"});
        table.DataTable().columns.adjust();
    });

    //////////////////Tabloya Özel/////////////////
    //select all işlemi event'i
    $('#select-all-' + es).on( "click", function(e) {
        if ($(this).is( ":checked" )) {
            table.DataTable().rows().select();        
        } else {
            table.DataTable().rows().deselect(); 
        }
    });

    //arrow key'ler ile hücrelerde gezinmeyi sağlar
    $(document).on('keyup', function ( e ) {
    if (e.keyCode === 40) { //key down
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.parent().next().children().eq(cellIndex).click();
    }else if(e.keyCode === 38){ //key up
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.parent().prev().children().eq(cellIndex).click();
    }else if(e.keyCode === 37){ //key left
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.prev().click();
    }else if(e.keyCode === 39){ //key right
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.next().click();
    }
    } );
    //////////////////Tabloya Özel-end/////////////////


   
    
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

function setNavTabSubPurchaseOrder(){
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

function formSubmitMessagePurchaseOrder(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
      event.preventDefault();
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
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

$(document).ready(function () {
    setPurchaseOrderPartDetailDatatable();
    //setHTMX();
    setNavTabSubPurchaseOrder();
    formSubmitMessagePurchaseOrder();
    
});
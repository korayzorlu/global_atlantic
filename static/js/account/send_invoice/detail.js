function setSendInvoicePartDetailDatatable(){
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
/**/let addDataHxGet = "/sale/inquiry_part_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    

    let order = [[1, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/account/api/send_invoice_items/editor/",
        table: tableId,
        idSrc: "id",
        fields: [{
                label: "trDescription",
                name: "trDescription",
            },
            {
                label: "quantity",
                name: "quantity",
            },
            {
                label: "unitPrice",
                name: "unitPrice",
            },
            {
                label: "totalPrice",
                name: "totalPrice",
            }
        ]
    });
    //////////////////Tabloya Özel-end/////////////////

    let buttons = [
        {
            // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"},
            className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        },
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
/**/let deleteDataUrl = "/account/send_invoice_part_delete/";
    let serverSide = false;
/**/let apiSource = '/account/api/send_invoice_items/?invoice=' + sendInvoiceId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            className: 'select-checkbox ps-1 pe-1',
            targets: 0,
            "width": "1%"
        },
        {"data" : "sequency","width": "1%", className:"ps-1 pe-1"},
        {"data" : "id", "visible":false},
        {"data" : "name", className:"text-start ps-1 pe-1", "width": "14%"},
        {"data" : "description", className:"text-start ps-1 pe-1", "width": "32%"},
        {"data" : "remark", className:"text-start ps-1 pe-1", "width": "20%"},
        {"data" : "trDescription", className:"editable ps-1 pe-1", "width": "20%"},
        {"data" : "quantity", className:"editable text-end ps-1 pe-1", "width": "1%"},
        {"data" : "unit", className:"ps-1 pe-1", "width": "1%"},
        {"data" : "unitPrice", className:"editable text-end ps-1 pe-1", "width": "5%", render: function (data, type, row, meta)
                            {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice", className:"editable text-end ps-1 pe-1", "width": "5%", render: function (data, type, row, meta)
                            {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "currency", "visible":false}
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
        scrollY : "30vh",
        scrollCollapse: true,
        // scroller: {
        //     loadingIndicator: true
        //   },
        fixedHeader: {
          header: true,
          headerOffset: $('#fixed').height()
        },
        responsive : true,
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

    new $.fn.dataTable.FixedHeader( table );
    
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);

    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);

        //tablo oluştuğunda loading spinner'ını kapatır
        $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
        });

        //sıra numaralarını ekler
        let i = 1;
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });

    });

    //////////////////Tabloya Özel/////////////////
    //Tıklanan hücrede edit yapılmasını sağlar.
    table.DataTable().on( 'click', 'tbody td.editable', function (e) {
        console.log(this);
        editor.inline(this, {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });
    });
  
    //yeni satır ekleme event'i
    table.DataTable().on('click', 'tbody td.row-edit', function (e) {
        editor.inline(table.DataTable().cells(this.parentNode, '*').nodes(), {
            submitTrigger: 1,
            submitHtml: '<i class="fa fa-play"/>',
            onBlur: 'submit'
        });
    });

    editor.on( 'submitSuccess', function ( e, json, data ) {
        var totalUnitPrice = 0
        var totalTotalPrice = 0
        table.DataTable().rows().every(function(){
            totalUnitPrice = totalUnitPrice + this.data()["unitPrice"];
            totalTotalPrice = totalTotalPrice + this.data()["totalPrice"];
        });
        $("#totalUnitPrice-" + elementTagSub + "-" + elementTagId).val(currencySymbol + " " + totalUnitPrice.toFixed(2));
        $("#totalTotalPrice-" + elementTagSub + "-" + elementTagId).val(currencySymbol + " " + totalTotalPrice.toFixed(2));
 
    });
    //////////////////Tabloya Özel-end/////////////////

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

            $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("show", {
                animation: false,
                spinner: "pulsar",
                maxSize: "150px",
                minSize: "150px",
                text: "Loading ...",
                background: "rgba(69, 83, 89, 0.6)",
                color: "#455359",
                textColor: "#fff"
            });

            

            let idList = []
            for(let i = 0; i < table.DataTable().rows({selected:true}).data().length; i++){
                idList.push(table.DataTable().rows({selected:true}).data()[i]["id"]);
            };

            htmx.ajax("POST", deleteDataUrl + idList, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
            setTimeout(function(){
                table.DataTable().ajax.reload()

                table.on( 'draw.dt', function () {
                    htmx.process(tableId);
                    $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                    animation: "fade"
                    });
                });
            },500);
        });
    };

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

    

};

function setSendInvoiceExpenseDetailDatatable(){
    let es = elementTagSub + "-" + elementTagId + "-expense";
    let id = sendInvoiceId

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
/**/let addDataHxGet = "/account/send_invoice_expense_add_in_detail/i_" + id + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[1, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/account/api/send_invoice_expenses/editor/",
        table: tableId,
        idSrc: "id",
        fields: [{
            label: "quantity",
            name: "quantity",
        },{
            label: "unitPrice",
            name: "unitPrice",
        },{
            label: "totalPrice",
            name: "totalPrice",
        }]
    });
    //////////////////Tabloya Özel-end/////////////////

    let buttons = [
        {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        tag: "img",
        attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
        className: "tableTopButtons inTableButtons",
        action: function ( e, dt, node, config ) {
            htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        }
        },
        // {   
        //     // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //     className: "tableTopButtons inTableButtons",
        //     tag: "img",
        //     attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
        //     extend: 'createInline',
        //     editor,
        //     formOptions: {
        //         submitTrigger: 1,
        //         submitHtml: '<i class="fa fa-play"/>',
        //         onBlur: 'submit'
        //     }
        // },
        {
            // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"},
            className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        },
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
/**/let deleteDataUrl = "/account/send_invoice_expense_delete/";
    let serverSide = false;
/**/let apiSource = '/account/api/send_invoice_expenses/?invoice=' + sendInvoiceId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%"},
        {"data" : "id", "visible" : false},
        {"data" : "code"},
        {"data" : "name"},
        {"data" : "quantity", className:"editable"},
        {"data" : "unit"},
        {"data" : "unitPrice", className:"editable",render: function (data, type, row, meta)
            {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice", className:"editable", render: function (data, type, row, meta)
            {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "currency", "visible" : false},
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
        scrollY : "33vh",
        scrollCollapse: true,
        // scroller: {
        //     loadingIndicator: true
        //   },
        fixedHeader: {
          header: true,
          headerOffset: $('#fixed').height()
        },
        responsive : true,
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
    

    //new $.fn.dataTable.FixedHeader(table);
    
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);

    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);

        //tablo oluştuğunda loading spinner'ını kapatır
        $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
        });

        //sıra numaralarını ekler
        let i = 1;
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });

    });

    //////////////////Tabloya Özel/////////////////
    //Tıklanan hücrede edit yapılmasını sağlar.
    table.DataTable().on( 'click', 'tbody td.editable', function (e) {
        console.log(this);
        editor.inline(this, {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });
    } );

    //yeni satır ekleme event'i
    table.DataTable().on('click', 'tbody td.row-edit', function (e) {
        editor.inline(table.DataTable().cells(this.parentNode, '*').nodes(), {
            submitTrigger: 1,
            submitHtml: '<i class="fa fa-play"/>',
            onBlur: 'submit'
        });
    });
    //////////////////Tabloya Özel-end/////////////////

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
    $("div.dataTables_processing").remove();
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

};

function formSubmitMessageSendInvoice(){
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
                    console.log("eburasıu");
                    setTimeout(function() {
                    $("#message-container-inside-" + ee + "-" + ei).fadeOut("slow");
                    }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
                };
            },
            error: function (xhr, status, error) {
                // Hata durumunda mesajı görüntüleyin
                var errorMessage = JSON.parse(xhr.responseText).message;
                $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-xmark-circle me-1"></i>' + errorMessage + '</div>');
            }
        });
      
    });
  
  
};

function setNavTabSubSendInvoice(){
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
    setSendInvoicePartDetailDatatable();
    setSendInvoiceExpenseDetailDatatable();
    setHTMX();
    setNavTabSubSendInvoice();
    //formSubmitMessageSendInvoice();
});
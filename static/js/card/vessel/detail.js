function setPersonDetailInVesselDatatable(){
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
/**/let addDataHxGet = "/card/person_add_in_detail_vessel/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    

    let order = [[1, 'asc']];

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
        {
            // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            className: "deleteData tableTopButtons inTableButtons delete-" + es + "",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"}
        },
        {
            // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
            className: "tableTopButtons inTableButtons",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/sync.svg"},
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
/**/let deleteDataUrl = "/card/person_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/persons?vessel=' + vesselId + '&format=datatables';
/**/let columns = [
                    {"data" : "id"},
                    {"data" : "name", render: function (data, type, row, meta)
                                    {return '<a hx-get="/card/person_update_in_vessel/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                                },  
                    {"data" : "title"},
                    {"data" : "email"},
                    {"data" : "phone"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": true,
        select: true,
        "pageLength": 20,
        scrollY : "12vh",
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

    table.DataTable().column(0).visible(false);

    //new $.fn.dataTable.FixedHeader( table );

    //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId);
    }, false);

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

function setEnginePartDetailDatatable(){
    let es = elementTagSub + "-" + elementTagId + "-enginePart";
    let id = vesselId

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
/**/let addDataHxGet = "/card/engine_part_add_in_detail/v_" + id + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[3, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
      ajax: "/card/api/engine_parts/editor/",
      table: tableId,
      idSrc: "id",
      fields: [
        {
          label: "category",
          name: "category",
        },
        {
            label: "serialNo",
            name: "serialNo",
        },
        {
            label: "cyl",
            name: "cyl",
        },
        {
            label: "description",
            name: "description",
        },
        {
            label: "version",
            name: "version",
        }
        ]
    });

    // editor_add = new $.fn.dataTable.Editor({
    //   ajax: "/sale/api/request_parts/editor/",
    //   table: tableId,
    //   idSrc: "id",
    //   fields: [{
    //       label: "part",
    //       name: "part.partNo",
    //       type: "select",
    //       options: options
    //   },{
    //         label: "quantity",
    //         name: "quantity",
    //   }]
    // });

    
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
        //   text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   extend: 'createInline',
        //   editor : editor_add,
        //   formOptions: {
        //       submitTrigger: 1,
        //       submitHtml: '<i class="fa fa-play"/>',
        //       onBlur: 'submit'
        //   }
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
/**/let deleteDataUrl = "/card/engine_part_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/engine_parts?vessel=' + vesselId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%"},
        {"data" : "id"},
        {"data" : "maker"},
        {"data" : "makerType"},
        // {"data" : "makerType.type", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/card/engine_part_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        //             },
        {"data" : "category", className:"editable"},
        {"data" : "serialNo", className:"editable"},
        {"data" : "cyl", className:"editable"},
        {"data" : "description", className:"editable"},
        {"data" : "version", className:"editable"}
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
        "pageLength": 20,
        scrollY : "30vh",
        scrollX : true,
        scrollCollapse: true,
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
        editor.inline(table.DataTable().cell(this).index(), {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });
        // editor.on('processing', function (e, json, data) {
        //     if(!$(".successSpin").length){
        //         $(".tableBox-inform-" + es + " .dt-buttons").append('<button type="button" class="dt-button tableTopButtons inTableButtons successSpin"><i class="fa-solid fa-gear fa-spin"></i></button>');
        //     };
            
        // });
        // editor.on('submitSuccess', function (e, json, data) {
        //     console.log("başarı");
        //     setTimeout(function() {
        //         $(".successSpin").remove();
        //     }, 1000);
            
        // });
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

function setOwnerDetailDatatable(){
    let es = elementTagSub + "-" + elementTagId + "-owner";
    let id = vesselId

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
/**/let addDataHxGet = "/card/owner_add_in_detail/v_" + id + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[3, 'asc']];

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
        //   text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   extend: 'createInline',
        //   editor : editor_add,
        //   formOptions: {
        //       submitTrigger: 1,
        //       submitHtml: '<i class="fa fa-play"/>',
        //       onBlur: 'submit'
        //   }
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
/**/let deleteDataUrl = "/card/owner_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/owners?vessel=' + vesselId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%"},
        {"data" : "id"},
        {"data" : "ownerCompany.name"},
        {"data" : "ownerCompany.country.formal_name"},
        {"data" : "ownerCompany.city.name"}
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
        "pageLength": 20,
        scrollY : "30vh",
        scrollX : true,
        scrollCollapse: true,
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
        editor.inline(table.DataTable().cell(this).index(), {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });
        // editor.on('processing', function (e, json, data) {
        //     if(!$(".successSpin").length){
        //         $(".tableBox-inform-" + es + " .dt-buttons").append('<button type="button" class="dt-button tableTopButtons inTableButtons successSpin"><i class="fa-solid fa-gear fa-spin"></i></button>');
        //     };
            
        // });
        // editor.on('submitSuccess', function (e, json, data) {
        //     console.log("başarı");
        //     setTimeout(function() {
        //         $(".successSpin").remove();
        //     }, 1000);
            
        // });
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

function setBillingDetailDatatable(){
    let es = elementTagSub + "-" + elementTagId + "-billing";
    let id = vesselId

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
/**/let addDataHxGet = "/card/billing_add_in_detail/v_" + id + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[2, 'desc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/card/api/billing_in_vessels/editor/",
        table: tableId,
        idSrc: "id",
        fields: [{
            label: "name",
            name: "name",
        },{
            label: "address",
            name: "address",
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
        //   text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   extend: 'createInline',
        //   editor : editor_add,
        //   formOptions: {
        //       submitTrigger: 1,
        //       submitHtml: '<i class="fa fa-play"/>',
        //       onBlur: 'submit'
        //   }
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
/**/let deleteDataUrl = "/card/billing_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/billing_in_vessels?vessel=' + vesselId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox ps-1 pe-1',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%", className:"ps-1 pe-1"},
        {"data" : "id", className:"ps-1 pe-1"},
        {"data" : "name", className:"editable text-start ps-1 pe-1"},
        {"data" : "address", className:"editable text-start ps-1 pe-1"}
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
        "pageLength": 20,
        scrollY : "30vh",
        scrollX : true,
        scrollCollapse: true,
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

function setVesselHistoryDetailDatatable(){
    let es = elementTagSub + "-" + elementTagId + "-companyHistory";
    let id = vesselId

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
/**/let addDataHxGet = "/card/billing_add_in_desail/v_" + id + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[3, 'desc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/card/api/billings/editor/",
        table: tableId,
        idSrc: "id",
        fields: [{
            label: "vessel",
            name: "vessel.id",
            def: function () { //tabloda gösterilmeyen ama gerekli olan alanı doldurur.
                return elementTagId
            }
        },{
            label: "name",
            name: "name",
        },{
            label: "address",
            name: "address",
        }]
    });
    //////////////////Tabloya Özel-end/////////////////

    let buttons = [
        // {
        // // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        // tag: "img",
        // attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
        // className: "tableTopButtons inTableButtons",
        // action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        // }
        // },
        // {   
        //   text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   extend: 'createInline',
        //   editor : editor_add,
        //   formOptions: {
        //       submitTrigger: 1,
        //       submitHtml: '<i class="fa fa-play"/>',
        //       onBlur: 'submit'
        //   }
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
/**/let deleteDataUrl = "/card/billding_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/vessel_histories/' + vesselId + '?format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%"},
        {"data" : "value"},
        {"data" : "date"},
        {"data" : "status"}
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
        "pageLength": 20,
        scrollY : "30vh",
        scrollX : true,
        scrollCollapse: true,
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
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    }, false);

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

function formSubmitMessageVessel(){
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
                console.log("eburasıu");
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

function setHTMXVessel(){
    let ee = elementTag;
    let ei = elementTagId;
    let es = elementTagSub + "-" + elementTagId + "-enginePart";
  
    let tableBox = $(".tableBox-" + ee);
    let tableId = "#table-" + ee;
    let table = $("#table-" + ee);
  
    //open
    htmx.on("htmx:afterSwap", (e) => {
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
        if (e.target.id == "addFormBlock-inform-d-justDetail-" + es) {
            document.getElementById("addFormBlock-inform-d-justDetail-" + es).innerHTML = "";
        };
    });
  
};

$(document).ready(function () {
    setPersonDetailInVesselDatatable();
    setEnginePartDetailDatatable();
    setOwnerDetailDatatable();
    setBillingDetailDatatable();
    setVesselHistoryDetailDatatable();
    setHTMXVessel();
    setNavTabSub();
    //formSubmitMessageVessel();
    
});


        
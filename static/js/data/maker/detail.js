function setMakerTypeDetailDatatable(){
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
/**/let addDataHxGet = "/data/maker_type_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[4, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/data/api/maker_types/editor/",
        table: tableId,
        idSrc: "id",
        fields: [{
            label: "maker",
            name: "maker.id",
            def: function () { //tabloda gösterilmeyen ama gerekli olan alanı doldurur.
                return elementTagId
            }
        },{
            label: "sourceCompany",
            name: "sourceCompany.id",
            def: function () { //tabloda gösterilmeyen ama gerekli olan alanı doldurur.
                return sourceCompanyId
            }
        },{
            label: "name",
            name: "name",
        }, {
            label: "type:",
            name: "type",
        },{
            label: "note:",
            name: "note",
        }]
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
        {   
            // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
            className: "tableTopButtons inTableButtons",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
            extend: 'createInline',
            editor,
            formOptions: {
                submitTrigger: 1,
                submitHtml: '<i class="fa fa-play"/>',
                onBlur: 'submit'
            }
        },
        {
            // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            className: "deleteData tableTopButtons inTableButtons delete-" + es + "",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"},
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

                table.DataTable().ajax.reload();

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
/**/let deleteDataUrl = "/data/maker_type_delete/";
    let serverSide = false;
/**/let apiSource = '/data/api/maker_types?maker=' + makerId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%"},
        {"data" : "id"},
        // {"data" : "name", className:"editable", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/data/maker_type_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        // },
        {"data" : "name", className:"editable"},
        {"data" : "type", className:"editable"},
        {"data" : "note", className:"editable"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": false,
        select: {
            style: 'multi',
            selector: 'td:first-child'
        },
        "pageLength": 20,
        scrollY : "32vh",
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
            };
            
        },
        "ajax" : apiSource,
        "columns" : columns
    });

    //sütun gizleme
    table.DataTable().column(2).visible(false);

    new $.fn.dataTable.FixedHeader( table );
    
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
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});


    
};

function setNavTabSubMaker(){
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

function formSubmitMessageMaker(){
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
    setMakerTypeDetailDatatable();
    setHTMX();
    setNavTabSubMaker();
    //formSubmitMessageMaker();

    
    
});
function setRequestPartAddDatatable(){
    let es = elementTagSub + "-" + elementTagId;
    let id = theRequestId

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
/**/let addDataHxGet = "/sale/request_part_add_in_detail/r_" + id + "/";
    //let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    let addDataHxTarget = "#addUpdateDataDialogXl";
    
    let order = [[2, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
      ajax: "/data/api/parts/editor/",
      table: tableId,
      idSrc: "id",
      fields: [{
          label: "theRequest",
          name: "theRequest.project.id",
          def: function () { //tabloda gösterilmeyen ama gerekli olan alanı doldurur.
              return elementTagId
          }
      },{
          label: "quantity",
          name: "quantity",
      }]
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
        // {
        //  // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        //  tag: "img",
        //  attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
        //  className: "tableTopButtons inTableButtons",
        //  action: function ( e, dt, node, config ) {
        //      htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        //  }
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
/**/let deleteDataUrl = "/sale/request_part_delete/";
    let serverSide = true;
/**/let apiSource = '/data/api/parts/?maker=' + makerId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "", className:"ps-1 pe-1","width": "3%"},
        {"data" : "id","visible":false},
        // {"data" : "part.partNo", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/sale/request_part_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        //             },
        {"data" : "partUniqueCode", className:"ps-1 pe-1","visible":false},
        {"data" : "partUnique", className:"ps-1 pe-1", render: function (data, type, row, meta){
            return data + '.' + String(row.partUniqueCode).padStart(3,0);
            }
        },
        {"data" : "maker", className:"ps-1 pe-1"},
        {"data" : "type", className:"ps-1 pe-1"},
        {"data" : "partNo", className:"ps-1 pe-1 fw-bold"},
        {"data" : "group", className:"ps-1 pe-1"},
        {"data" : "description", className:"ps-1 pe-1"},
        {"data" : "techncialSpecification", className:"ps-1 pe-1"},
        {"data" : "manufacturer", className:"ps-1 pe-1"},
        {"data" : "crossRef", className:"ps-1 pe-1"},
        {"data" : "unit", className:"ps-1 pe-1"},
        {"data" : "stockCode", className:"ps-1 pe-1"},
        {"data" : "stock", className:"ps-1 pe-1"},
        {"data" : "warehouse", className:"ps-1 pe-1"}
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
        scrollY : "50vh",
        scrollX : true,
        scrollCollapse: true,
        colReorder: true,
        // scroller: {
        //     loadingIndicator: true
        //   },
        fixedHeader: false,
        responsive : false,
        language: { search: '', searchPlaceholder: "Search..." },
        dom : 'Blfrtip',
        buttons : buttons,
        columnDefs: [{
            "defaultContent": "",
            "targets": "_all"
          }],
        initComplete: function () {
            $(tableId + '_wrapper div.dataTables_filter input').focus();
        },
        preDrawCallback: function() {
            $(tableId + ' tbody').append($(
                `
                <div class="row w-100">
                     <div class="col-md-12 text-center tableLoading">
                        
                    </div>
                </div>
                `
            ));

            $(".tableLoading").busyLoad("show", {
                animation: false,
                spinner: "pulsar",
                maxSize: "150px",
                minSize: "150px",
                text: "Loading...",
                background: "rgba(69, 83, 89, 0)",
                color: "#455359",
                textColor: "#fff"
            });
        },
        drawCallback: function() {
            var api = this.api();
            var rowCount = api.rows({page: 'current'}).count();
            
            // for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
            //   $(tableId + ' tbody').append($("<tr ></tr>"));
            // }
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

function formSubmitMessageRequestPartAdd(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl;
    console.log(u);
  
    $("#form-" + ee +  "-" + ei + "-add-2").submit(function (event) {
      //spinner başlatır
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

      event.preventDefault();

      var formData = $(this).serializeArray();

      tableRequestParts = $("#table-" + elementTagSub + "-" + elementTagId);
      
      for(let i = 0; i < tableRequestParts.DataTable().rows({selected:true}).data().length; i++){
        formData.push({name: "requestParts", value: tableRequestParts.DataTable().rows({selected:true}).data()[i]["id"]});
      };

      //console.log(tableRequestParts.DataTable().rows({selected:true}).data());
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: formData,
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
                setTimeout(function() {

                    addUpdateDataModalXl.hide();

                    $("#table-requestPart-" + elementTagId).DataTable().ajax.reload(function(){
                        htmx.process("#tale-requestPart-" + elementTagId);
                    },false);

                    setTimeout(function() {
                        //spinner durdurur
                        $("body").busyLoad("hide", {
                        animation: "fade"
                        });
                    }, 1000);
            
                }, 1500);
                $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                setTimeout(function() {
                  $("#message-container-inside-" + ee + '-' + ei + "-add-2").fadeOut("slow");
                }, 1500); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            }
        },
        error: function (xhr, status, error) {
          //spinner durdurur
          $("body").busyLoad("hide", {
            animation: "fade"
          });
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-xmark-circle me-1"></i>At least one part must be selected!</div>');
        }
      });
      
  
      
  
    });
};

$(document).ready(function () {
    setRequestPartAddDatatable();
    //formSubmitMessageRequestPartAdd();
});
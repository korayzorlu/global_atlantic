function setProjectItemAddDatatable(){
    let es = elementTagSub + "-" + elementTagId;
    let id = projectId

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
/**/let addDataHxGet = "/purchasing/project_item_add_in_detail/r_" + id + "/";
    //let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    let addDataHxTarget = "#addUpdateDataDialogXl";
    
    let order = [[2, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/data/api/parts/editor/",
        table: tableId,
        idSrc: "id",
        fields: [
            {
                label: "project",
                name: "project.id",
                def: function () { //tabloda gösterilmeyen ama gerekli olan alanı doldurur.
                    return elementTagId
                }
            },
            {
                label: "quantity",
                name: "quantity",
            }
        ]
    });
    
    //////////////////Tabloya Özel-end/////////////////

    let buttons = [
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
/**/let deleteDataUrl = "/purchasing/project_item_delete/";
    let serverSide = true;
/**/let apiSource = '/data/api/parts?format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "","width": "3%"},
        {"data" : "id","visible":false},
        // {"data" : "part.partNo", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/purchasing/project_item_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        //             },
        {"data" : "partUniqueCode", className:"double-clickable","visible":false},
        {"data" : "partUnique", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
            return data + '.' + String(row.partUniqueCode).padStart(3,0);
            }
        },
        {"data" : "maker", className:"editable-add"},
        {"data" : "type", className:"editable-add"},
        {"data" : "partNo", className:"editable-add fw-bold"},
        {"data" : "group"},
        {"data" : "description"},
        {"data" : "techncialSpecification"},
        {"data" : "manufacturer"},
        {"data" : "crossRef"},
        // {"data" : "", "width" : "10%", render: function (data, type, row, meta){
        //     return '<input type="number" id="requestPartQuantityForm" class="form-control form-control-sm" value="1">';
        // }
        // },
        {"data" : "unit"}
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
        //"pageLength": 20,
        scrollY : "50vh",
        scrollX : true,
        scrollCollapse: true,
        scroller: {
            loadingIndicator: true
          },
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
        initComplete: function () {
            $(tableId + '_wrapper div.dataTables_filter input').focus();
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

function formSubmitMessageProjectItemAdd(){
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

      tableProjectItems = $("#table-" + elementTagSub + "-" + elementTagId);
      
      for(let i = 0; i < tableProjectItems.DataTable().rows({selected:true}).data().length; i++){
        formData.push({name: "requestParts", value: tableProjectItems.DataTable().rows({selected:true}).data()[i]["id"]});
      };

      //console.log(tableProjectItems.DataTable().rows({selected:true}).data());
  
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
    setProjectItemAddDatatable();
    //formSubmitMessageProjectItemAdd();
});
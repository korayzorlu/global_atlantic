function setRequestPartDetailDatatable(){
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
    
    let order = [[1, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
      ajax: "/sale/api/request_parts/editor/",
      table: tableId,
      idSrc: "id",
      fields: [{
          label: "sequency",
          name: "sequency",
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
            text: 'data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"',
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
        },
        {
          // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/exchange.svg","data-mdb-toggle":"tooltip","data-mdb-placement":"right","title":"Send to inquiry"},
          className: "addToInquiryData tableTopButtons inTableButtons addToInquiry-" + es + ""
        },
    ];

    let addToInquiryDataButtonId = ".addToInquiryData";

    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/sale/request_part_delete/";
    let serverSide = false;
/**/let apiSource = '/sale/api/request_parts?theRequest=' + theRequestId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            searchable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "sequency","width": "1%", className : "editable ps-1 pe-1"},
        {"data" : "id"},
        // {"data" : "part.partNo", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/sale/request_part_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        //             },
        {"data" : "partNo", "width": "15%", className:"text-start ps-1 pe-1"},
        {"data" : "description", className:"text-start ps-1 pe-1", "width": "50%"},
        {"data" : "quantity","width" : "3%", className:"editable text-center ps-1 pe-1", orderable: false},
        {"data" : "unit", className:"text-center ps-1 pe-1", "width": "1%"},
        {"data" : "stockCode", className:"text-start ps-1 pe-1", "width": "5%"},
        {"data" : "stock", className:"text-end ps-1 pe-1", "width": "2%"},
        {"data" : "warehouse", className:"text-start ps-1 pe-1", "width": "10%"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": false,
        select: {
          style: 'single',
          selector: 'td:first-child'
        },
        //"pageLength": 20,
        paging: false,
        scrollY : "52vh",
        scrollX : true,
        scrollCollapse: true,
        //rowReorder: true,
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
            
            // for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
            //   $(tableId + ' tbody').append($("<tr ></tr>"));
            // }
        },
        "ajax" : apiSource,
        "columns" : columns
      });
    
    //sütun gizleme
    table.DataTable().column(2).visible(false);

    //new $.fn.dataTable.FixedHeader(table);
    
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);

    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);

        $(".duplicateQuantityButton").on("click", function(){
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
          let requestPartId = $(this).attr("data-pk");
          htmx.ajax("POST", "/sale/request_part_quantity_duplicate/" + requestPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
          
          setTimeout(function() {
            table.DataTable().ajax.reload()

            table.on( 'draw.dt', function () {
                htmx.process(tableId);
                $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                  animation: "fade"
                });
            });
          },1500);
        });

        //tablo oluştuğunda loading spinner'ını kapatır
        $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
        });

        //sıra numaralarını ekler
        // let i = 1;
        // table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
        //     this.data(i++);
        // });

    });

    
    //////////////////Tabloya Özel/////////////////
    //Tıklanan hücrede edit yapılmasını sağlar.
    table.DataTable().on( 'click', 'tbody td.editable', function (e) {
        // editor.edit(table.DataTable().cell(this).index(), {
        //   focus: null
        // });
        editor.inline(table.DataTable().cell(this).index(), {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });

        $('.DTE_Field input[type="text"]').attr('autocomplete', 'off');

        
        
        // editor.on('processing', function (e, json, data) {
        //     if(!$(".successSpin").length){
        //         $(".tableBox-inform-" + es + " .dt-buttons").append('<button type="button" class="dt-button tableTopButtons inTableButtons successSpin"><i class="fa-solid fa-gear fa-spin"></i></button>');
        //     };
            
        // });
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
            

            // setTimeout(function() {
            //     $(".successSpin").remove();
            // }, 1000);
            
        });
    } );


    // table.DataTable().on( 'row-reorder', function (e, diff, edit) {
    //   //tablo oluşurken loading spinner'ını açar
    //   $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("show", {
    //     animation: false,
    //     spinner: "pulsar",
    //     maxSize: "150px",
    //     minSize: "150px",
    //     text: "Loading ...",
    //     background: "rgba(69, 83, 89, 0.6)",
    //     color: "#455359",
    //     textColor: "#fff"
    //   });

    //   //işlemler
    //   idList = []
    //   oldList = []
    //   newList = []
    //   rowDataList = []
    //   for (var i = 0, ien = diff.length; i < ien; i++) {
    //     let rowData = table.DataTable().row(diff[i].node).data();
    //     rowDataList.push(rowData);
    //     //console.log(rowData["theRequest"]["project"]["id"]);
    //     idList.push(rowData["id"])
    //     oldList.push(diff[i].oldData)
    //     newList.push(diff[i].newData)
    //     //console.log("part: " + rowData["part"]["partNo"] + " old: " + diff[i].oldData + " new: " + diff[i].newData);
    //     //console.log(rowData["id"]);
    //     //htmx.ajax("POST", "/sale/request_part_reorder/p_" + rowData["id"] + "_old_" + diff[i].oldData + "_new_" + diff[i].newData + "/", {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
    //   };
    //   htmx.ajax("POST", "/sale/request_part_reorder/r_" + rowDataList[0]["theRequestId"] + "_p_" + idList + "_old_" + oldList + "_new_" + newList, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
      
    //   setTimeout(function() {
    //     table.DataTable().ajax.reload()

    //     table.on( 'draw.dt', function () {
    //         htmx.process(tableId);
    //         $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
    //           animation: "fade"
    //         });
    //     });
    //   },1500);
    
    // });

    // editor.on('postCreate postRemove', function () {
    //   console.log("taşındı");
    //   table.DataTable().ajax.reload(null, false);
    // });
    // editor.on('initCreate', function () {
    //   // Enable order for create
    //   console.log("çalıştııı");
    //   editor.field('sequency').enable();
    // });
    // editor.on('initEdit', function () {
    //   // Disable for edit (re-ordering is performed by click and drag)
    //   editor.field('sequency').disable();
    // });

    //seçili satırın quantity değerini tüm satırlara kopyalar
    $(".duplicateSelectedQuantityButton").on("click", function(){
      if(table.DataTable().row({selected:true}).data()["id"]){
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
        let requestPartId = table.DataTable().row({selected:true}).data()["id"];
        htmx.ajax("POST", "/sale/request_part_quantity_duplicate/" + requestPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        
        setTimeout(function() {
          table.DataTable().ajax.reload()
  
          table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          });
        },1500);
      };
      
    });
    
    //////////////////Tabloya Özel-end/////////////////

    //virgül ile girilen ondalık sayıları noktaya çevririr
    editor.on( 'preSubmit', function ( e, json, data, label ) {
      function bul(obj, key) {
          for (var key in obj) {
            if (typeof obj[key] === "object") {
              var outcome = bul(obj[key], key);
              if (outcome !== undefined) {
                return outcome;
              }
            } else if (key === searchKey) {
              return obj[key];
            }
          }
      };
      function degistir(obj, key, newValue) {
          for (var key in obj) {
            if (typeof obj[key] === "object") {
              degistir(obj[key], key, newValue);
            } else if (key === searchKey) {
              obj[key] = newValue;
            }
          }
      };

      var searchKey = "quantity";
      var outcome = bul(json, searchKey);

      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };
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
    
    //inquiry'e gönder
    $(addToInquiryDataButtonId).click(function (){
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

      htmx.ajax("GET", "/sale/request_part_add_to_inquiry/" + table.DataTable().row({selected:true}).data()["id"], {target : "#addUpdateDataDialog"});

      setTimeout(function(){
          table.DataTable().ajax.reload(function() {
              htmx.process(tableId);
          }, false);
          $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
          });
      },1000);
      
      
    });

    //veri silme butonu
    if(deleteDataButton){
        $(deleteDataButtonId).click(function (){
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
          //işlemler
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
              $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          },1000);
          
          
        });
    };

    // default loading spinner'ı gizler
    $("div.dataTables_processing").remove();
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});



    //htmx.ajax('GET', addDataHxGet, addDataHxTarget);
    /////////////////////////tabloya özel-end/////////////////////////


    
};

function formSubmitMessageRequest(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
    
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
      console.log(ee + ei);
      event.preventDefault();

      console.log("iiiiytythghg");
  
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
  
    $("#form-" + ee +  "-" + ei + "-add-3").submit(function (event) {
      event.preventDefault();
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
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
            
                setTimeout(function() {
            
                  let eSub = ee +  "-" + ei + "-add-3";
            
                  let navTagSub = $("#navTag-" + eSub);
                  let tabPaneSub = $("#tabPane-" + eSub);
            
                  navTagSub.prev().children("a").addClass("active");
                  tabPaneSub.prev().addClass("show active");
                  
                  navTagSub.prev().children("a").children("button").show();
                  $("#table-" + ee).DataTable().columns.adjust();
                  
                  navTagSub.remove();
                  tabPaneSub.remove();
            
                  setTimeout(function() {
                    $("body").busyLoad("hide", {
                      animation: "fade"
                    });
                  }, 1000);
            
                }, 2000);
                $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                console.log("eburasıu");
                setTimeout(function() {
                  $("#message-container-inside-" + ee + '-' + ei + "-add-3").fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            }
        },
        error: function (xhr, status, error) {
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
        }
      });
      
  
      
  
    });
};

function setNavTabSubRequest(){
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

// var options = []
    
// fetch('/data/api/parts?maker=' + maker + '&type=' + type + '&format=datatables', {method : "GET"})
//   .then((response) => {
//   return response.json();
//   })
//   .then((data) => {
//     console.log(data["data"][0]["id"]);
//     for(let i = 0; i < data["data"].length; i++){
//       options.push({label : data["data"][i]["partNo"] + " - " + data["data"][i]["description"], value : data["data"][i]["id"]})
//     };

//     setRequestPartDetailDatatable();
    
// });

$(document).ready(function () {
    setRequestPartDetailDatatable();
    //setHTMX();
    setNavTabSubRequest();
    formSubmitMessageRequest();
    
});
function setAcceptanceServiceCardDetailDatatable(){
  let es = elementTagSub + "-" + elementTagId + "-serviceCard";
  let id = acceptanceId

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
/**/let addDataHxGet = "/service/acceptance_service_card_add_in_detail/o_" + id + "/";
  let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
  
  let order = [[2, 'asc']];

  //////////////////Tabloya Özel/////////////////
  //Datatable Editor için editor'ü tanımlar.
  let editor = new $.fn.dataTable.Editor({
      ajax: "/service/api/acceptance_service_cards/editor/",
      table: tableId,
      idSrc: "id",
      fields: [
          {
              label: "remark",
              name: "remark",
          },
          {
              label: "quantity",
              name: "quantity",
          },
          {
              label: "unitPrice1",
              name: "unitPrice1",
          },
          {
              label: "profit",
              name: "profit",
          },
          {
              label: "discount",
              name: "discount",
          },
          {
              label: "tax",
              name: "tax",
          },
          {
              label: "note",
              name: "note",
            }
      ]
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
/**/let deleteDataUrl = "/service/acceptance_service_card_delete/";
  let serverSide = false;
/**/let apiSource = '/service/api/acceptance_service_cards?acceptance=' + acceptanceId + '&format=datatables';
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
      {"data" : "code"},
      {"data" : "name"},
      {"data" : "about"},
      {"data" : "remark", className:"editable"},
      {"data" : "quantity", className:"editable"},
      {"data" : "unit"},
      {"data" : "unitPrice1", className:"editable", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      },
      {"data" : "profit", className:"editable", render: function (data, type, row, meta)
                      {return (data).toFixed(2) + " %"}
      },
      {"data" : "unitPrice2", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      },
      {"data" : "discount", className:"editable", render: function (data, type, row, meta)
                      {return (data).toFixed(2) + " %"}
      },
      {"data" : "unitPrice3", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      },
      {"data" : "tax", className:"editable", render: function (data, type, row, meta)
                      {return (data).toFixed(2) + " %"}
      },
      {"data" : "taxPrice", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      },
      {"data" : "totalPrice", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      },
      {"data" : "note", className:"editable ps-1 pe-1", orderable: false, "width":"6%"},
      {"data" : "currency","visible":false}
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
      scrollY : "47vh",
      scrollX : true,
      scrollCollapse: true,
      fixedHeader: {
        header: true,
        headerOffset: $('#fixed').height()
      },
      responsive : true,
      language: { search: '', searchPlaceholder: "Search..." },
      dom : 'Blfrtip',
      buttons : buttons,
      fixedHeader : {
        header: false,
        footer: false
      },
      columnDefs: [
          {
              "defaultContent": "",
              "targets": "_all"
          },
          { width: "200px", targets: 5 }
      ],
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
          let idList = []
          for(let i = 0; i < table.DataTable().rows({selected:true}).data().length; i++){
              idList.push(table.DataTable().rows({selected:true}).data()[i]["id"]);
          };

          htmx.ajax("POST", deleteDataUrl + idList, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
          
          //tabloyu yeniler
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
          
          setTimeout(function(){
              table.DataTable().ajax.reload()

              table.on( 'draw.dt', function () {
                  htmx.process(tableId);
                  $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                  animation: "fade"
                  });
              });
          },500);
          //tabloyu yeniler-end

      });
  };

  // default loading spinner'ı gizler
  $("div.dataTables_processing").remove();
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});



  
};

function formSubmitMessageAcceptance(){
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

function setNavTabSubAcceptance(){
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
    setAcceptanceServiceCardDetailDatatable();
    setHTMX();
    setNavTabSubAcceptance();
    formSubmitMessageAcceptance();
    
});
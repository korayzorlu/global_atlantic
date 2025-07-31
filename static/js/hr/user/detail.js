function setEducationAddDatatable(){
  let es = elementTagSub + "-" + elementTagId + "-education";

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

  let addFormBlockSubID = "#addFormBlock-inform-" + es;

  let tableId = '#table-' + es;
  let table = $('#table-' + es);
/**/let addDataHxGet = "/hr/education_add_in_detail/u_" + profileId + "/";
  let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
  
  let order = [[1, 'asc']];

  let buttons = [
      {
      // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
      className: "tableTopButtons inTableButtons",
      tag: "img",
      attr: {src:"/static/images/icons/datatable/add-file.svg"},
      action: function ( e, dt, node, config ) {
          htmx.ajax('GET', addDataHxGet, addDataHxTarget);
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
/**/let deleteDataUrl = "/hr/education_delete/";
  let serverSide = false;
/**/let apiSource = '/api/educations?educationProfile=' + profileId + '&format=datatables';
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
                  {"data" : "school", render: function (data, type, row, meta)
                                  {return '<a hx-get="/hr/education_update_in_user/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                              },  
                  {"data" : "department"},
                  {"data" : "education_status"},
                  {"data" : "startDate"},
                  {"data" : "finishDate"}
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
      dom : 'Blfrtip',
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

  table.DataTable().column(2).visible(false);

  //new $.fn.dataTable.FixedHeader( table );

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
  //select all işlemi event'i
  $('#select-all-' + es).on( "click", function(e) {
      if ($(this).is( ":checked" )) {
          table.DataTable().rows().select();        
      } else {
          table.DataTable().rows().deselect(); 
      }
  });
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
          table.DataTable().ajax.reload(function() {
              htmx.process(tableId);
          }, false);
          
          console.log(idList);
      });
  };

  // default loading spinner'ı gizler
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});

};

function setAdditionalPaymentAddDatatable(){
  let es = elementTagSub + "-" + elementTagId + "-salary";

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

  let addFormBlockSubID = "#addFormBlock-inform-" + es;

  let tableId = '#table-' + es;
  let table = $('#table-' + es);
/**/let addDataHxGet = "/hr/additional_payment_add_in_detail/u_" + profileId + "/";
  let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
  
  let order = [[1, 'asc']];

  let buttons = [
      {
      // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
      className: "tableTopButtons inTableButtons",
      tag: "img",
      attr: {src:"/static/images/icons/datatable/add-file.svg"},
      action: function ( e, dt, node, config ) {
          htmx.ajax('GET', addDataHxGet, addDataHxTarget);
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
/**/let deleteDataUrl = "/hr/additional_payment_delete/";
  let serverSide = false;
/**/let apiSource = '/api/aditional_payments?additionalPaymentProfile=' + profileId + '&format=datatables';
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
                  {"data" : "amount", render: function (data, type, row, meta)
                                  {return '<a hx-get="/hr/aditional_payment_update_in_user/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                              },  
                  {"data" : "payment_type"},
                  {"data" : "additionalPaymentDate"},
                  {"data" : "currency"}
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
      dom : 'Blfrtip',
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

  table.DataTable().column(2).visible(false);
  table.DataTable().column(6).visible(false);

  //new $.fn.dataTable.FixedHeader( table );

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
  //select all işlemi event'i
  $('#select-all-' + es).on( "click", function(e) {
      if ($(this).is( ":checked" )) {
          table.DataTable().rows().select();        
      } else {
          table.DataTable().rows().deselect(); 
      }
  });
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
          table.DataTable().ajax.reload(function() {
              htmx.process(tableId);
          }, false);
          
          console.log(idList);
      });
  };

  // default loading spinner'ı gizler
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});

};

function formSubmitMessageUser(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
        event.preventDefault();
        console.log("sdsg");
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

function setNavTabSubUser(){
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
/**/setEducationAddDatatable();
/**/setAdditionalPaymentAddDatatable();
    setHTMX();
    setNavTabSubUser();
    formSubmitMessageUser();

    
    
});
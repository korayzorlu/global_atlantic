
function setProjectItemPurchasingInquiryAddDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let es = elementTagSub + "-" + elementTagId + "-item";

    //tablo oluşurken loading spinner'ını açar
    $("#tabPane-" + es).busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: "#fff",
      color: "#455359",
      textColor: "#455359"
    });

    let tableId = '#table-' + es;
    let table = $('#table-' + es);

    let order = [[3, 'asc']];
  
    let buttons = [
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          className: "tableTopButtons inTableButtons",
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
          action: function ( e, dt, node, config ) {
            $(".tableBox-" + es + " .dataTables_scrollBody").busyLoad("show", {
              animation: false,
              spinner: "pulsar",
              maxSize: "150px",
              minSize: "150px",
              text: "Loading ...",
              background: "rgba(69, 83, 89, 0.6)",
              color: "#455359",
              textColor: "#fff"
            });

            table.DataTable().ajax.reload(function() {
              
            });
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];
  

    let serverSide = false;
/**/let apiSource = '/purchasing/api/project_items?project=' + elementTagId + '&format=datatables';
/**/let columns = [
                    { 
                      orderable: false,
                      className: 'select-checkbox',
                      targets: 0,
                      "width": "1%"
                    },
                    {"data" : "","width": "3%"},
                    {"data" : "id"},
                    {"data" : "name"},
                    {"data" : "description"},
                    {"data" : "quantity"}
                    
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
      scrollY : "35vh",
      scrollCollapse: true,
      fixedHeader: {
        header: true,
        headerOffset: $('#fixed').height()
      },
      responsive : false,
      language: {
        search: '',
        searchPlaceholder: "Search..."
        //processing: '<i class="fa fa-circle-notch fa-spin fa-3x fa-fw" style="z-index:99999;"></i>'
      },
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
      initComplete: function () {
        $(tableId + '_wrapper div.dataTables_filter input').focus();
      },
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td>"));
        }
      },
      "ajax" : apiSource,
      "columns" : columns
    });

    //sütun gizleme
    table.DataTable().column(2).visible(false);

    new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    }, false);
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        
        //tablo oluştuğunda loading spinner'ını kapatır
        $("#tabPane-" + es).busyLoad("hide", {
          animation: "fade"
        });

        //sıra numaralarını ekler
        let i = 1;
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(i++);
        });

    });

    // table.on( 'search.dt', function () {
    //   table.DataTable().row({selected:true}).invalidate().draw();
    // });
    
    //tabloyu sağa ve sola yaslamak için parent elementin paddingini kaldır
    $('.box:has(' + tableId + '_wrapper)').css({
      'padding': '12px 0'
    });

    //tablo uznluğu seçimindeki yazıları kaldırır
    $("div.dataTables_wrapper div.dataTables_length label").contents().filter(function() {
      return this.nodeType === 3 && (this.nodeValue.includes("Show") || this.nodeValue.includes("entries"));
    }).remove();

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

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

};

function setCompanyPurchasingInquiryAddDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let es = elementTagSub + "-" + elementTagId + "-inquiry";

    //tablo oluşurken loading spinner'ını açar
    $("#tabPane-" + elementTag + "-" + elementTagId + "-add-2").busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: "#f2f2f2",
      color: "#455359",
      textColor: "#455359"
    });

    let addFormBlockID = "#addFormBlock-" + es;
    let addFormBlockSubID = "#tabContSub-" + es;

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/card/company_add/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[3, 'asc']];
  
    let buttons = [
        {
          text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          className: "tableTopButtons inTableButtons",
          action: function ( e, dt, node, config ) {
            $(".tableBox-" + es + " .dataTables_scrollBody").busyLoad("show", {
              animation: false,
              spinner: "pulsar",
              maxSize: "150px",
              minSize: "150px",
              text: "Loading ...",
              background: "rgba(69, 83, 89, 0.6)",
              color: "#455359",
              textColor: "#fff"
            });

            table.DataTable().ajax.reload(function() {
              
            });
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];
  

    let serverSide = false;
/**/let apiSource = '/card/api/companies?supplierCheck=True&format=datatables';
/**/let columns = [ 
                    { 
                        orderable: false,
                        className: 'select-checkbox',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "","width": "3%"},
                    // {"data" : "id", render: function (data, type, row, meta){
                    //   return '<input class="form-check-input suppliersCheckbox" type="checkbox" value="' + data + '" id="flexCheckDefault" name="suppliers" style="position:relative;margin-top:.19em;margin-left:0;">';
                    // }
                    // },
                    {"data" : "id"},
                    {"data" : "name"},
                    {"data" : "country.international_formal_name"},
                    {"data" : "city.name"}
    ];

    table.DataTable({
      order : order,
      "serverSide" : serverSide,
      "processing" : true,
      "autoWidth": true,
      // select: {
      //   style: 'multi',
      //   selector: 'td:first-child'
      // },
      select: {
        style: 'multi',
        selector: 'td:first-child'
      },
      deferRender : true,
      rowId: 'id',
      paging: false,
      scrollY : "35vh",
      scrollCollapse: true,
      fixedHeader: {
        header: true,
        headerOffset: $('#fixed').height()
      },
      responsive : false,
      language: {
        search: '',
        searchPlaceholder: "Search..."
        //processing: '<i class="fa fa-circle-notch fa-spin fa-3x fa-fw" style="z-index:99999;"></i>'
      },
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
      initComplete: function () {
        $(tableId + '_wrapper div.dataTables_filter input').focus();
      },
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td>"));
        };
        
      },
      "ajax" : apiSource,
      "columns" : columns
    });

    //sütun gizleme
    table.DataTable().column(2).visible(false);

    new $.fn.dataTable.FixedHeader(table);
  
    //tablo her yüklendiğinde oluşan eylemler.
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    }, false);
    
    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        
        //tablo oluştuğunda loading spinner'ını kapatır
        $("#tabPane-" + elementTag + "-" + elementTagId + "-add-2").busyLoad("hide", {
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
    
    //tabloyu sağa ve sola yaslamak için parent elementin paddingini kaldır
    $('.box:has(' + tableId + '_wrapper)').css({
      'padding': '12px 0'
    });

    //tablo uznluğu seçimindeki yazıları kaldırır
    $("div.dataTables_wrapper div.dataTables_length label").contents().filter(function() {
      return this.nodeType === 3 && (this.nodeValue.includes("Show") || this.nodeValue.includes("entries"));
    }).remove();

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

    

};

function setNavTabSubPurchasingInquiryAdd(){
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

function setNavTabSubDetailPurchasingInquiryAdd(){
  let eSub = elementTag + "-" + elementTagId + "-add-2";

  if(elementTag == "quotationAdd"){
    var efSub = "inquiry";
  }else if(elementTag == "inquiryAdd"){
    var efSub = "request";
  }else if(elementTag == "purchasingInquiryAdd"){
    var efSub = "project";
  };
  
  let uSub = pageUrl;
  
  let navTagSub = $("#navTag-" + eSub);
  let navTagLinkSub = $("#navTagLink-" + eSub);
  let tabPaneSub = $("#tabPane-" + eSub);
  let removeNavSub = $("#removeNav-" + eSub);
  let sideBarButtonSub = $(".nav-list li ." + eSub);

  $(".mainNavLinkSubDetail-" + efSub).removeClass("active");
  $(".mainTabPaneSubDetail-" + efSub).removeClass("show active");

  $("#nav-" + efSub + "-" + elementTagId + "-add").append(navTagSub);
  $("#tab-" + efSub + "-" + elementTagId + "-add").append(tabPaneSub);
  navTagLinkSub.addClass("active");
  tabPaneSub.addClass("show active");

  $(".mainNavLinkSubDetail:not(.active)").children("button").hide();

  removeNavSub.click(function(){
    navTagSub.prev().children("a").addClass("active");
    //tabPaneSub.prev().addClass("show active");
    $("#tabPane-" + efSub + "-" + elementTagId + "-add-1").addClass("show active");
    console.log(tabPaneSub);
    
    navTagSub.prev().children("a").children("button").show();
    
    navTagSub.remove();
    tabPaneSub.remove();

    sideBarButtonSub.attr("hx-swap", "afterbegin");

    $("#createInquiryButton").removeClass("d-none");
      
  });

  navTagLinkSub.on("shown.bs.tab", function(e){
      $(e.target).children("button").show();
      console.log($(e.target));

      $(e.relatedTarget).children("button").hide();

      history.pushState({}, null, uSub);
  });

  navTagSub.css({"display" : "block"});
};


function formSubmitMessagePurchasingInquiryAdd(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl;
    let sk = sessionKey;
  
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

      tableSuppliers = $("#table-" + elementTagSub + "-" + elementTagId + "-inquiry");
      tableParts = $("#table-" + elementTagSub + "-" + elementTagId + "-item");

      for(let i = 0; i < tableSuppliers.DataTable().rows({selected:true}).data().length; i++){
        formData.push({name: "suppliers", value: tableSuppliers.DataTable().rows({selected:true}).data()[i]["id"]});
      };
      for(let i = 0; i < tableParts.DataTable().rows({selected:true}).data().length; i++){
        formData.push({name: "items", value: tableParts.DataTable().rows({selected:true}).data()[i]["id"]});
      };
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: formData,
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
                setTimeout(function() {
            
                  let eSub = ee +  "-" + ei + "-add-2";
            
                  let navTagSub = $("#navTag-" + eSub);
                  let tabPaneSub = $("#tabPane-" + eSub);
            
                  navTagSub.prev().children("a").addClass("active");
                  $("#tabPane-request-" + elementTagId + "-add-1").addClass("show active");
                  
                  navTagSub.prev().children("a").children("button").show();
                  $("#table-" + ee).DataTable().columns.adjust();
                  
                  navTagSub.remove();
                  tabPaneSub.remove();

                  $("#createInquiryButton").removeClass("d-none");

                  if($("#navTag-inquiry").length > 0){
                    $("#navTagLink-request").removeClass("active");
                    $("#tabPane-request").removeClass("active show");
                    $("#navTagLink-inquiry").addClass("active");
                    $("#tabPane-inquiry").addClass("active show");

                    fetch('/sale/api/inquiries?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                      .then((response) => {
                        return response.json();
                      })
                      .then((data) => {
                        htmx.ajax("GET", "/sale/inquiry_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                        window.history.pushState({}, '', "/sale/inquiry_update/" + data["data"][0]["id"] + "/");
                      });
                  }else{
                    htmx.ajax("GET", "/sale/inquiry_data", {target:"#tabCont", swap:"afterbegin"});
                    setNavTabSubInquiryAdd();
                    fetch('/sale/api/inquiries?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                      .then((response) => {
                        return response.json();
                      })
                      .then((data) => {
                        htmx.ajax("GET", "/sale/inquiry_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                        window.history.pushState({}, '', "/sale/inquiry_update/" + data["data"][0]["id"] + "/");
                      });
                  };
                  
                  setTimeout(function() {
                    //spinner durdurur
                    $("body").busyLoad("hide", {
                      animation: "fade"
                    });
                  }, 1000);
            
                }, 2000);
                $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                setTimeout(function() {
                  $("#message-container-inside-" + ee + '-' + ei + "-add-2").fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
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
/**/setProjectItemPurchasingInquiryAddDataTable();
/**/setCompanyPurchasingInquiryAddDataTable();
    setNavTabSubDetailPurchasingInquiryAdd();
    //formSubmitMessagePurchasingInquiryAdd();

  //spinner durdurur
  $("body").busyLoad("hide", {
    animation: "fade"
  });
});





                    
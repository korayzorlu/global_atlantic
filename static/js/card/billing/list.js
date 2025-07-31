
function setBillingDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag;

    //tablo oluşurken loading spinner'ını açar
    $("#tabPane-" + ef).busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: window.getComputedStyle($(".tab-content")[0]).backgroundColor,
      color: "#455359",
      textColor: "#455359"
    });

    let addFormBlockID = "#addFormBlock-" + ef;
    let addFormBlockSubID = "#tabContSub-" + ef;

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);
/**/let addDataHxGet = "/card/billing_add/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[3, 'asc']];
  
    let buttons = [
        {
          // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/add-file.svg"},
          className: "tableTopButtons inTableButtons",
          action: function ( e, dt, node, config ) {
            htmx.ajax('GET', addDataHxGet, {target : addDataHxTarget, swap : "afterbegin", "push-url" : "true"});
            window.history.pushState({}, '', addDataHxGet);
          }
        },
        {
          // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
          className: "deleteData tableTopButtons inTableButtons delete-" + ef + "",
          tag: "img",
          attr: {src:"/static/images/icons/datatable/deletefile.svg"},
        },
        // {
        //   extend: "csvHtml5",
        //   // text: '<i class="fa-solid fa-file-csv" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to csv file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/csv-file.svg"},
        // },
        // {
        //   extend: "excelHtml5",
        //   // text: '<i class="fa-solid fa-file-excel" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to excel file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/xls.svg"},
        // },
        // {
        //   extend: "pdfHtml5",
        //   // text: '<i class="fa-solid fa-file-pdf" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to pdf file"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/pdf.svg"},
        // },
        // {
        //   extend: "print",
        //   // text: '<i class="fa-solid fa-print" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Print"></i>',
        //   className: "tableTopButtons inTableButtons",
        //   tag: "img",
        //   attr: {src:"/static/images/icons/datatable/printer.svg"},
        // },
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          className: "tableTopButtons inTableButtons",
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
          action: function ( e, dt, node, config ) {
            $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("show", {
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
              $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];
  
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/card/billing_delete/";
    let serverSide = true;
/**/let apiSource = '/card/api/billings?format=datatables';
/**/let columns = [
                      {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable ps-1 pe-1"},
                    {"data" : "vessel", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "name", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                        //return '<a href="/card/vessel_update/' + row.id + '/" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';
                        return '<a hx-get="/card/billing_update/' + row.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                    },
                    {"data" : "hesapKodu", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "vatNo", className:"double-clickable text-start ps-1 pe-1"},
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
      scrollY : "77vh",
      scrollCollapse: true,
      colReorder: true,
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
      initComplete: function () {
        $(tableId + '_wrapper div.dataTables_filter input').focus();
      },
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td></tr>"));
        }
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

      //tablo oluştuğunda loading spinner'ını kapatır
      $("#tabPane-" + ef).busyLoad("hide", {
        animation: "fade"
      });

      //sıra numaralarını ekler
      let i = 1;
      table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
        let data = table.DataTable().row(this).data();
  
    /**/htmx.ajax('GET', '/card/billing_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
        window.history.pushState({}, '', '/card/billing_update/' + data["id"] + '/');
    });

    //select all işlemi event'i
    $('#select-all-' + ef).on( "click", function(e) {
      if ($(this).is( ":checked" )) {
          table.DataTable().rows().select();        
      } else {
          table.DataTable().rows().deselect(); 
      }
    });
    
    //veri silme butonu
    if(deleteDataButton){
        $(deleteDataButtonId).click(function (){
            
            let idList = []
            for(let i = 0; i < table.DataTable().rows({selected:true}).data().length; i++){
                idList.push(table.DataTable().rows({selected:true}).data()[i]["id"]);
            };
            htmx.ajax("GET", deleteDataUrl + idList, "#addUpdateDataDialog");
            console.log(idList);
        });
    };
    
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

function setNavTabBilling(){
  let e = elementTag;
  let ef = elementTag;
  let u = pageUrl;

  let navTag = $("#navTag-" + e);
  let navTagLink = $("#navTagLink-" + e);
  let tabPane = $("#tabPane-" + e);
  let removeNav = $("#removeNav-" + e);
  let sideBarButton = $(".nav-list li ." + e);

  $(".mainNavLink").removeClass("active");
  $(".mainTabPane").removeClass("show active");

  $("#tabNav").append(navTag);
  $("#tabCont").append(tabPane);
  navTagLink.addClass("active");
  tabPane.addClass("show active");

  $(".mainNavLink:not(.active)").children("button").hide();

  sideBarButton.attr("hx-swap", "none");
  $(".home-section").css({"overflow" : "hidden"});

  $("#table-" + e).DataTable().columns.adjust();

  removeNav.click(function(){
      navTag.prev().children("a").addClass("active");
      tabPane.prev().addClass("show active");
      
      navTag.prev().children("a").children("button").show();

      if(navTag.prev().attr("id") == "dashboardNavTag"){
        $(".home-section").css({"overflow" : "hidden"});
      };
      
      navTag.remove();
      tabPane.remove();

      sideBarButton.attr("hx-swap", "afterbegin");

      /******sekme stroage kontrolü******/
      var mainTabState = JSON.parse(localStorage.getItem("mainTabState"));
    
      if(mainTabState.some(item => item.app === "card" && item.model === "billing")){
        let tabIndex = mainTabState.findIndex(item => item.app === "card" && item.model === "billing");
        if (tabIndex > -1) {
          mainTabState.splice(tabIndex, 1);
        };
        localStorage.setItem('mainTabState', JSON.stringify(mainTabState));
      };
      /******sekme stroage kontrolü-end******/
      
  });

  navTagLink.on("shown.bs.tab", function(e){
    $(e.target).children("button").show();
    $(e.relatedTarget).children("button").hide();

    $("#table-" + ef).DataTable().columns.adjust();

    $(".home-section").css({"overflow" : "hidden"});

    history.pushState({}, null, u);
  });

  navTag.css({"display" : "block"});
};


$(document).ready(function () {
/**/setBillingDataTable();
    setNavTabBilling();
    setNavTabSub();
    setHTMX();

    /******sekme stroage kontrolü******/
    // var mainTabState = JSON.parse(localStorage.getItem("mainTabState"));
    
    // if(! mainTabState.some(item => item.app === "card" && item.model === "billing")){
    //   mainTabState.push({app : "card", model : "billing", url : "/card/billing_data/"});
    //   localStorage.setItem('mainTabState', JSON.stringify(mainTabState));
    // };
    /******sekme stroage kontrolü-end******/

});






function setPartItemDataTable(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag;
    let es = elementTagSub + "-" + elementTagId;
    let ei = elementTagId;

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
/**/let addDataHxGet = "/warehouse/part_item_add/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[2, 'desc']];
  
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
          tag: "img",
          attr: {src:"/static/images/icons/datatable/deletefile.svg"},
          className: "deleteData tableTopButtons inTableButtons delete-" + ef + ""
        },
        {
          // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/sync.svg"},
          className: "tableTopButtons inTableButtons",
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

            table.DataTable().columns.adjust().draw();
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];

    //////////////////Tabloya Özel/////////////////
    
    function format(d) {
      // `d` is the original data object for the row

      var partItems = d.items;

      return (
        ` 
          <!--<div class="row">
            <div class="col-md-12 text-center fs-5">
              <i class="fa-solid fa-chevron-down"></i>
            </div>
          </div>-->

          <table id="partItem-${d.id}" class="table table-hover">
            <thead>
              <tr class="bg-blue-esms fw-bold">
                <td class="text-white d-none">ID</td>
                <td class="text-white">Stock Code</td>
                <td class="text-white">Stock Date</td>
                <td class="text-white">Invoice</td>
                <td class="text-white">Warehouse</td>
                <td class="text-white">Location</td>
                <td class="text-white">Unit</td>
                <td class="text-white">Quantity</td>
                <td class="text-white">Unit Cost</td>
                <td class="text-white">Currency</td>
              </tr>
            <thead>
            <tbody>
              ${partItems.map(item => `
                <tr class="">
                  <td class="partItemCell d-none">${item.id}</td>
                  <td class="partItemCell">${item.itemNo}</td>
                  <td class="partItemCell">${item.itemDate}</td>
                  <td class="partItemCell">${item.invoice}</td>
                  <td class="partItemCell">${item.warehouse}</td>
                  <td class="partItemCell">${item.location}</td>
                  <td class="partItemCell">${item.unit}</td>
                  <td class="partItemCell">${item.quantity}</td>
                  <td class="partItemCell"><span class="">${item.cost.toLocaleString('tr-TR', { currency: item.currency, minimumFractionDigits: 2 })}</span></td>
                  <td class="partItemCell">${item.currency}</td>
                </tr>
              `).join('')}
            <tbody>
          </table>
        `
      )

      

      
    };
    //////////////////Tabloya Özel-end/////////////////
  
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/warehouse/part_item_delete/";
    let serverSide = true;
/**/let apiSource = '/warehouse/api/part_item_groups?format=datatables';
/**/let columns = [
                    {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable", "visible":false},
                    {"data" : "partUniqueCode", className:"double-clickable","visible":false},
                    {"data" : "partUnique", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                        return data + '.' + String(row.partUniqueCode).padStart(3,0);
                      }
                    },
                    {"data" : "maker", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "type", className:"double-clickable ps-1 pe-1"},
                    {"data" : "name", className:"double-clickable ps-1 pe-1"},
                    {"data" : "barcode", className:"double-clickable ps-1 pe-1"},
                    {"data" : "quantity", className:"double-clickable ps-1 pe-1"},
                    {"data" : "items", className:"double-clickable ps-1 pe-1","visible":false}
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
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        }
      },
      "ajax" : apiSource,
      "columns" : columns
    });

  
    new $.fn.dataTable.FixedHeader(table);

    

    //////////////////Tabloya Özel/////////////////
    // Add event listener for opening and closing details
    //+ butonu ile tablo üzerinde özet detaylar görüntüler
    table.on('click', '.double-clickable', function (e) {
      let tr = e.target.closest('tr');
      let row = table.DataTable().row(tr);

      if (row.child.isShown()) {
          // This row is already open - close it
          $(tr).removeClass("bg-red-esms");
          $(tr).find("td").removeClass("text-white");
          row.child.hide();
      }
      else {
          // Open this row
          $(tr).addClass("bg-red-esms");
          $(tr).find("td").addClass("text-white");
          console.log(format(row.data()));
          row.child(format(row.data())).show();
      };
      htmx.process(tableId);
    });
   
    //////////////////Tabloya Özel-end/////////////////

    //////////////////Tabloya Özel/////////////////
    // part item detail
    table.on('click', '.partItemCell', function (e) {
      let row = e.target.closest('tr');
      let itemId = row.querySelector('td').textContent;
      
      htmx.ajax('GET', '/warehouse/part_item_update/' + itemId + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/warehouse/part_item_update/' + itemId + '/');

      htmx.process(tableId);
    });
   
    //////////////////Tabloya Özel-end/////////////////
  
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
        let j= 1;
        table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
            this.data(j++);
        });

    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
      let data = table.DataTable().row(this).data();

  /**/htmx.ajax('GET', '/warehouse/part_item_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
      window.history.pushState({}, '', '/warehouse/art_item_update/' + data["id"] + '/');
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
          setTimeout(function(){
            table.DataTable().ajax.reload(function() {
                htmx.process(tableId);
            }, false);
          },1000);
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

function setNavTabPartItem(){
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

function setNavTabSubPartItem(){
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


function setHTMXPartItem(){
  let ee = elementTag;
  let ei = elementTagId;

  let tableBox = $(".tableBox-" + ee);
  let tableId = "#table-" + ee;
  let table = $("#table-" + ee);

  //open
  htmx.on("htmx:afterSwap", (e) => {
    if(e.detail.target.id == "tabContSub-" + ee){
      table.on( 'draw.dt', function () {
        htmx.process(tableId);
        $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
          animation: "fade"
        });
      });
    };
    if (e.detail.target.id == "addUpdateDataDialog-" + ee) {
      console.log(location.href);
      //addUpdateDataModal.show();
    };
  });
  //submitted
  htmx.on("htmx:beforeSwap", (e) => {
    if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
      e.detail.shouldSwap = false;
    };
    if (e.detail.target.id == "addUpdateDataDialog-" + ee && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      //addUpdateDataModal.hide();
      e.detail.shouldSwap = false;
      $(tableId).DataTable().ajax.reload(function(){
        htmx.process(tableId);
      },false);
    };
  });
  //cancelled
  htmx.on("hidden.bs.modal", (e) => {
    if (e.target.id == "addUpdateDataDialog-" + ee) {
      console.log(location.href);
      document.getElementById("addUpdateDataDialog-" + ee).innerHTML = "";
    };
  });

};

$(document).ready(function () {
/**/setPartItemDataTable();
    setNavTabPartItem();
    setNavTabSubPartItem();
    setHTMXPartItem();

});







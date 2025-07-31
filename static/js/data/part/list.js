
function setPartDataTable(){/**/
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
/**/let addDataHxGet = "/data/part_add/";
    let addDataHxTarget = addFormBlockSubID;

    let order = [[2, 'desc']];
  
    var buttons = [
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
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];

    if(dataAuthorizationList.includes("data")){
      var buttons = [
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
          tag: "img",
          attr: {src:"/static/images/icons/datatable/xls.svg"}, 
          className: "tableTopButtons inTableButtons",
          action: function ( e, dt, node, config ) {
            //window.location.href = "/sale/quotation_all_excel/";
            //htmx.ajax("GET", "/sale/quotation_all_excel/", {target : "#addUpdateDataDialog-inform"});
            htmx.ajax("GET", "/data/part_filter_excel/", {target : "#addUpdateDataDialogXl"});
          }
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
            
            table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-" + ef + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
            });
          }
        }
    ];
    };
  
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/data/part_delete/";
    let serverSide = true;
/**/let apiSource = '/data/api/parts/?format=datatables';
/**/let columns = [
                    {
                        orderable: false,
                        searchable: false,
                        className: 'select-checkbox ps-1 pe-1',
                        targets: 0,
                        "width": "1%"
                    },
                    {"data" : "", className:"double-clickable ps-1 pe-1"},
                    {"data" : "id", className:"double-clickable"},
                    {"data" : "partUniqueCode", className:"double-clickable"},
                    {"data" : "partUnique", className:"double-clickable ps-1 pe-1", render: function (data, type, row, meta){
                        return data + '.' + String(row.partUniqueCode).padStart(3,0);
                      }
                    },
                    {"data" : "maker", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "type", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "group", className:"double-clickable ps-1 pe-1"},
                    {"data" : "partNo", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "description", className:"double-clickable text-start ps-1 pe-1", render: function (data, type, row, meta){
                      return '<a hx-get="/data/part_update/' + row.id + '/" hx-target="' + addFormBlockSubID + '" hx-swap="afterbegin" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                    },
                    {"data" : "techncialSpecification", className:"double-clickable text-start ps-1 pe-1"},
                    {"data" : "crossRef", className:"double-clickable ps-1 pe-1"},
                    {"data" : "ourRef", className:"double-clickable ps-1 pe-1"},
                    {"data" : "drawingNr", className:"double-clickable ps-1 pe-1"},
                    {"data" : "manufacturer", className:"double-clickable ps-1 pe-1"},
                    {"data" : "unit", className:"double-clickable ps-1 pe-1"}
                    
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
      //paging: true,
      //"deferRender": true,
      scrollY : "77vh",
      scrollCollapse: true,
      // scroller: {
      //   loadingIndicator: true
      // },
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
      drawCallback: function() {
        var api = this.api();
        var rowCount = api.rows({page: 'current'}).count();
        
        for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        }
      },
      "ajax" : apiSource,
      "columns" : columns
    });

    //sütun gizleme
    table.DataTable().column(2).visible(false);
    table.DataTable().column(3).visible(false);
  
    //new $.fn.dataTable.FixedHeader(table);
  
    // //tablo her yüklendiğinde oluşan eylemler.
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
      let pageLength = table.DataTable().page.len();
      let page = table.DataTable().page();
      let i = 1 + (page * pageLength);
      table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

    });

    //çift tıklama ile detay sayfalarına gider
    table.on('dblclick', '.double-clickable', function () {
        let data = table.DataTable().row(this).data();
  
    /**/htmx.ajax('GET', '/data/part_update/' + data["id"] + '/', {target : addFormBlockSubID, swap : "afterbegin", "push-url" : "true"});
        window.history.pushState({}, '', '/data/part_update/' + data["id"] + '/');
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

function setHTMXPart(){
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

function mikroPartStatus(){
  let eSub = elementTag + "-" + elementTagId;
  let removeNavSub = $("#removeNav-" + eSub);

  //spinner başlatır
  $("body").busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Connecting to Mikro ...",
      background: "rgba(69, 83, 89, 0.6)",
      color: "#455359",
      textColor: "#fff"
  });
  
  var wsMikro = new WebSocket(
    (window.location.protocol === 'https:' ? 'wss://' : 'ws://')
    + window.location.host
    + '/ws/mikro_status/'
    + 121
    + '/'
  );

  wsMikro.onmessage = function(e) {
      const wsMikroData = JSON.parse(e.data);
      
      if(wsMikroData.status == "connected"){
          cariKodAlert.update({color:"success"});
          document.getElementById('cariKodAlert').innerHTML = '<i class="fas fa-satellite-dish me-3"></i>' + wsMikroData.message + '<button id="cariKodAlertClose" type="button" class="btn-close"></button>';
      }else if(wsMikroData.status == "success"){
          cariKodAlert.update({color:"success"});
          document.getElementById('cariKodAlert').innerHTML = '<i class="fas fa-circle-check me-3"></i>' + wsMikroData.message + '<button id="cariKodAlertClose" type="button" class="btn-close"></button>';
      }else if(wsMikroData.status == "not_found"){
          cariKodAlert.update({color:"warning"});
          document.getElementById('cariKodAlert').innerHTML = '<i class="fas fa-triangle-exclamation me-3"></i>' + wsMikroData.message + '<button id="cariKodAlertClose" type="button" class="btn-close"></button>';
      }else{
          cariKodAlert.update({color:"danger"});
          document.getElementById('cariKodAlert').innerHTML = '<i class="fas fa-triangle-exclamation me-3"></i>' + wsMikroData.message + '<button id="cariKodAlertClose" type="button" class="btn-close"></button>';
      };

      $("#cariKodAlertClose").on("click", function(){
        cariKodAlert.hide();
      });

      if(wsMikroData.process == "reload"){
          let ee = elementTag;
          let ei = elementTagId;
          let u = pageUrl

          let navTagSub = $("#navTag-" + ee + "-" + ei);
          let tabPaneSub = $("#tabPane-" + ee + "-" + ei);

          navTagSub.remove();
          tabPaneSub.remove();

          htmx.ajax("GET", "/card/company_update/" + elementTagId + "/", {target:"#tabContSub-company", swap:"afterbegin"});
          window.history.pushState({}, '', "/card/company_update/" + elementTagId + "/");
      };

      //spinner durdurur
      $("body").busyLoad("hide", {
          animation: "fade"
      });

      cariKodAlert.show();
        
      // setTimeout(function() {
      //   cariKodAlert.hide();
      // },4000);
  };
  

  wsMikro.onopen = function() {
      console.log('WebSocket bağlantısı başarıyla kuruldu.');
  };
  wsMikro.onerror = function(error) {
      console.error('WebSocket hatası:', error.message);
  };

  wsMikro.onclose = function () {
    console.log("Websocket kapatıldı!")
  };
  

  removeNavSub.click(function(){
      wsMikro.close();
  });

  window.onload = function() {
    wsMikro.close();
  };

  window.onbeforeunload = function() {
      wsMikro.close();
  };
};

$(document).ready(function () {
    setPartDataTable();
    setNavTab();
    setNavTabSub();
    setHTMXPart();
    //mikroPartStatus();
});

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

    let tableId = '#table-' + ef;
    let table = $('#table-' + ef);
/**/let addDataHxGet = "/data/part_add/";
    let addDataHxTarget = addFormBlockID;

    let order = [[2, 'asc']];
  
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
          tag: "img",
          attr: {src:"/static/images/icons/datatable/deletefile.svg"},
          className: "deleteData tableTopButtons inTableButtons delete-" + ef + ""
        },
        {
          extend: "csvHtml5",
          // text: '<i class="fa-solid fa-file-csv" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to csv file"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/csv-file.svg"},
          className: "tableTopButtons inTableButtons",
        },
        {
          extend: "excelHtml5",
          // text: '<i class="fa-solid fa-file-excel" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to excel file"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/xls.svg"},
          className: "tableTopButtons inTableButtons",
        },
        {
          extend: "pdfHtml5",
          // text: '<i class="fa-solid fa-file-pdf" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to pdf file"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/pdf.svg"},
          className: "tableTopButtons inTableButtons",
        },
        {
          extend: "print",
          // text: '<i class="fa-solid fa-print" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Print"></i>',
          tag: "img",
          attr: {src:"/static/images/icons/datatable/printer.svg"},
          className: "tableTopButtons inTableButtons",
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
  
    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + ef;
/**/let deleteDataUrl = "/data/part_delete/";
    let serverSide = true;
/**/let apiSource = '/data/api/parts?format=datatables';
/**/let columns = [
                    {"data" : ""},
                    {"data" : "id"},
                    {"data" : "partUniqueCode"},
                    {"data" : "partUnique","data2":"partUniqueCode", render: function (data, type, row, meta){
                        return data.code + '.' + String(row.partUniqueCode).padStart(3,0);
                      }
                    },
                    {"data" : "maker.name"},
                    {"data" : "type.type"},
                    {"data" : "type.name"},
                    {"data" : "partNo", render: function (data, type, row, meta){
                        return '<a hx-get="/data/part_update/' + row.id + '/" hx-target="' + addFormBlockID + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                    },
                    {"data" : "unit"},
                    {"data" : "crossRef"},
                    {"data" : "ourRef"},
                    {"data" : "description"}         
    ];

    table.DataTable({
      order : order,
      "serverSide" : serverSide,
      "processing" : true,
      "autoWidth": true,
      "select" : true,
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
          $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
        }
      },
      "ajax" : apiSource,
      "columns" : columns
    });

    table.DataTable().column(1).visible(false);
    table.DataTable().column(2).visible(false);
  
    new $.fn.dataTable.FixedHeader(table);
  
    //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId);
    }, false);
  
    table.on( 'draw.dt', function () {
      htmx.process(tableId);

      //tablo oluştuğunda loading spinner'ını kapatır
      $("#tabPane-" + ef).busyLoad("hide", {
        animation: "fade"
      });

      //sıra numaralarını ekler
      let i = 1;
      table.DataTable().cells(null, 0, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

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




$(document).ready(function () {
    setPartDataTable();
    setNavTab();
    setHTMX();

});
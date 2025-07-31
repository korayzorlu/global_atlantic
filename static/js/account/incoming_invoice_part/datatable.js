function setRequestPartDatatable(){
    let es = elementTagSub + "-" + elementTagId;

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

    let addFormBlockSubID = "#addFormBlock-inform-d-justDetail-" + es;

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/account/incoming_invoice_part_add/";
    let addDataHxTarget = addFormBlockSubID;
    
    let order = [[1, 'asc']];

    let buttons = [
        // {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        // className: "tableTopButtons inTableButtons",
        // action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        // }
        // },
        {
            text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        },
        {
            text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
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
    let serverSide = false;
/**/let apiSource = '/sale/api/request_parts?theRequest__isnull=true&sessionKey=' + sessionKey + '&format=datatables';
/**/let columns = [
                    {"data" : "id"},
                    {"data" : "part.partNo", render: function (data, type, row, meta)
                                    {return '<a hx-get="/sale/request_part_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                                },
                    {"data" : "part.description"},
                    {"data" : "quantity"},
                    {"data" : "part.unit"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": true,
        "select" : true,
        "pageLength": 20,
        scrollY : "18vh",
        scrollCollapse: true,
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

    table.DataTable().column(0).visible(false);

    //new $.fn.dataTable.FixedHeader(table);

    //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId);
    }, false);

    table.on( 'draw.dt', function () {
        htmx.process(tableId);
        $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
        });
    });
    
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

$(document).ready(function () {
    setRequestPartDatatable();
    setHTMX();
    setNavTabSub();
    formSubmitMessage();
});
function setMakerTypeDetailDatatable(){
    let es = elementTagSub;

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/data/maker_type_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-" + es;
    

    let order = [[1, 'asc']];

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
              table.DataTable().ajax.reload()
            }
          }
    ];

    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/data/maker_type_delete/";
    let serverSide = false;
/**/let apiSource = '/data/api/maker_types?maker=' + makerId + '&format=datatables';
/**/let columns = [
        {"data" : "id"},
        {"data" : "name", render: function (data, type, row, meta)
                        {return '<a hx-get="/data/maker_type_update/' + row.id + '/" hx-target="#addFormBlock-inform-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                    },  
        {"data" : "type"},
        {"data" : "note"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": true,
        "select" : true,
        "pageLength": 50,
        scrollY : "25vh",
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
        "ajax" : apiSource,
        "columns" : columns
      });

    table.DataTable().column(0).visible(false);

    new $.fn.dataTable.FixedHeader( table );
    
    //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId);
    }, false);

    table.on( 'draw.dt', function () {
        htmx.process(tableId);
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
            setTimeout(function(){
                table.DataTable().ajax.reload(function() {
                    htmx.process(tableId);
                }, false);
            },500);
            
            console.log(idList);
        });
    };


    
};

$(document).ready(function () {
    setMakerTypeDetailDatatable();
    setHTMX();
    
});
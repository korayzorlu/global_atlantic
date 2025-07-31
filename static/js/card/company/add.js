function setPersonAddInCompanyDatatable(){
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

    let addFormBlockSubID = "#addFormBlock-inform-" + es;

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/card/person_add_in_company/";
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
            // text: '<i class="fa-regular fa-trash-can" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            className: "deleteData tableTopButtons inTableButtons delete-" + es + "",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"},
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
/**/let deleteDataUrl = "/card/person_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/persons?company__isnull=true&sessionKey=' + sessionKey + '&format=datatables';
/**/let columns = [
                    {"data" : "id"},
                    {"data" : "name", render: function (data, type, row, meta)
                                    {return '<a hx-get="/card/person_update_in_company/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                                },  
                    {"data" : "title"},
                    {"data" : "email"},
                    {"data" : "phone"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": true,
        select: true,
        "pageLength": 20,
        scrollY : "30vh",
        scrollX : true,
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

    //new $.fn.dataTable.FixedHeader( table );

    
    

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

function formSubmitMessageCompanyAdd(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
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
            let eSub = "company-new";

            let navTagSub = $("#navTag-" + eSub);
            let tabPaneSub = $("#tabPane-" + eSub);

            navTagSub.prev().children("a").addClass("active");
            tabPaneSub.prev().addClass("show active");
            
            navTagSub.prev().children("a").children("button").show();
            $("#table-" + ee).DataTable().columns.adjust();
            
            navTagSub.remove();
            tabPaneSub.remove();

            // const backdrop = document.querySelector('#full-backdrop');
            // backdrop.remove();
            // loadingFull.remove();

            
            
            fetch('/card/api/companies?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                .then((response) => {
                return response.json();
                })
                .then((data) => {
                console.log(data["data"][0]["id"]);
                htmx.ajax("GET", "/card/company_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                window.history.pushState({}, '', "/card/company_update/" + data["data"][0]["id"] + "/");
                
                })
            
            setTimeout(function() {
                $("body").busyLoad("hide", {
                animation: "fade"
                });
            }, 1000);
        

        }, 2000);
      
    });
  
  
};

$(document).ready(function () {
    setPersonAddInCompanyDatatable();
    setHTMX();
    setNavTabSub();
    //formSubmitMessageCompanyAdd();

});
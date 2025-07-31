function setQuotationPartDetaiOIClDatatable(){
    let es = elementTagSub;

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/sale/quotation_part_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    

    let order = [[1, 'asc']];

    let buttons = [
        // {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        // className: "tableTopButtons inTableButtons",
        // action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        // }
        // },
        // {
        //     text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
        //     className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        // },
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
/**/let deleteDataUrl = "/sale/quotation_part_delete/";
    let serverSide = false;
/**/let apiSource = '/sale/api/quotation_parts?quotation=' + quotationId + '&format=datatables';
/**/let columns = [
        {"data" : "id"},
        {"data" : "inquiryPart.requestPart.part.partNo"},
        {"data" : "inquiryPart.requestPart.part.description", "className": "editable"},
        {"data" : "quantity"},
        {"data" : "inquiryPart.requestPart.part.unit"},
        {"data" : "unitPrice1", render: function (data, type, row, meta)
                        {return (data).toFixed(2)}
        },
        {"data" : "totalPrice1", render: function (data, type, row, meta)
                        {return (data).toFixed(2)}
        },
        {"data" : "profit"},
        {"data" : "unitPrice2", render: function (data, type, row, meta)
                        {return (data).toFixed(2)}
        },
        {"data" : "totalPrice2", render: function (data, type, row, meta)
                        {return (data).toFixed(2)}
        },
        {"data" : "discount"},
        {"data" : "unitPrice3", render: function (data, type, row, meta)
                        {return (data).toFixed(2)}
        },
        {"data" : "totalPrice3", render: function (data, type, row, meta)
                        {return (data).toFixed(2)}
        },
        {"data" : "availability"},
        {"data" : "availabilityType"}
    ];

    table.DataTable({
        order : order,
        "serverSide" : serverSide,
        "processing" : true,
        "autoWidth": true,
        select: true,
        "pageLength": 20,
        scrollY : "18vh",
        scrollX : true,
        scrollCollapse: true,
        fixedHeader: {
          header: true,
          headerOffset: $('#fixed').height()
        },
        responsive : false,
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
              $(tableId + ' tbody').append($("<tr ><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"));
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

     ///////////////////////////tabloya özel///////////////////////////
     table.on('click', 'td', function () {
        console.log(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]);
        $("#partGroupInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["group"]);
        $("#partManufacturerInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["manufacturer"]);
        $("#partCrossRefInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["crossRef"]);
        $("#partOurRefInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["ourRef"]);
        $("#partQuantityInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["quantity"]);
        $("#partBuyingPriceInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["buyingPrice"]);
        $("#partRetailPriceInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["retailPrice"]);
        $("#partDealerPriceInfoInput").val(table.DataTable().row(this).data()["inquiryPart"]["requestPart"]["part"]["dealerPrice"]);
        $("#partlast3SalesInfoInput-1").val('( 06-23-2023 = 50.15000 EUR ) M/V ANA N');
        $("#partlast3SalesInfoInput-2").val('( 07-10-2021 = 47.22000 EUR ) M/V ANA N');
        $("#partlast3SalesInfoInput-3").val('( 27-09-2021 = 47.22000 EUR ) M/V ANA N');
    });


    /////////////////////////tabloya özel-end/////////////////////////




    
};

function formSubmitMessageOrderInProcess(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
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
  
    
};

$(document).ready(function () {
    setQuotationPartDetaiOIClDatatable();
    setHTMX();
    setNavTabSub();
    formSubmitMessageOrderInProcess();
    
});
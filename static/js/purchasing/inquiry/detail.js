function setPurchasingInquiryItemDetailDatatable(){
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

    let tableId = '#table-' + es;
    let table = $('#table-' + es);
/**/let addDataHxGet = "/purchasing/inquiry_part_add_in_detail/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
    
    let order = [[1, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    let editor = new $.fn.dataTable.Editor({
        ajax: "/purchasing/api/inquiry_items/editor/",
        table: tableId,
        idSrc: "id",
        fields: [
            {
                label: "sequency",
                name: "sequency",
            },
            {
                label: "quantity",
                name: "quantity",
            },
            {
                label: "unitPrice",
                name: "unitPrice",
            },
            {
                label: "totalPrice",
                name: "totalPrice",
            },
            {
                label: "availability",
                name: "availability",
            },
            {
                label: "note",
                name: "note",
              },{
                label: "remark",
                name: "remark",
              }
        ]
    });
    //////////////////Tabloya Özel-end/////////////////
    var buttons = [
        // {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        // className: "tableTopButtons inTableButtons",
        // action: function ( e, dt, node, config ) {
        //     htmx.ajax('GET', addDataHxGet, addDataHxTarget);
        // }
        // },
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
/**/let deleteDataUrl = "/purchasing/inquiry_item_delete/";
    let serverSide = false;
/**/let apiSource = '/purchasing/api/inquiry_items?inquiry=' + inquiryId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            className: 'select-checkbox',
            targets: 0,
            "width": "1%"
        },
        {"data" : "sequency",className:"editable"},
        {"data" : "id", "visible" : false},
        // {"data" : "requestPart.part.partNo", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/sale/inquiry_part_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        // },
        {"data" : "name"},
        {"data" : "description"},
        {"data" : "quantity", className:"editable", orderable: false},
        {"data" : "unit"},
        {"data" : "unitPrice", className:"editable", attr: {"type": "number"}, render: function (data, type, row, meta)
                            {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice",className:"editable", render: function (data, type, row, meta)
                            {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "availability", className:"editable", orderable: false, render: function (data, type, row, meta)
                        {return data + " " + row.availabilityType + "s"}
        },
        {"data" : "note", className:"editable ps-1 pe-1", orderable: false, "width": "6%"},
        {"data" : "remark", className:"editable ps-1 pe-1", orderable: false, "width": "6%"},
        {"data" : "availabilityType", "visible" : false},
        {"data" : "currency", "visible" : false}
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
        //"pageLength": 20,
        paging: false,
        scrollY : "50vh",
        scrollCollapse: true,
        fixedHeader: {
          header: true,
          headerOffset: $('#fixed').height(),
          footer: false
        },
        responsive : true,
        language: { search: '', searchPlaceholder: "Search..." },
        dom : 'Bfrtip',
        buttons : buttons,
        columnDefs: [{
          "defaultContent": "",
          "targets": "_all"
        }],
        drawCallback: function() {
            var api = this.api();
            var rowCount = api.rows({page: 'current'}).count();

            let totalQuantity = 0

            for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
              $(tableId + ' tbody').append($("<tr ></tr>"));
            };
        },
        "ajax" : apiSource,
        "columns" : columns
      });
    


    //new $.fn.dataTable.FixedHeader( table );
    
    //tablo her yüklendiğinde oluşan eylemler.
    // table.DataTable().ajax.reload(function() {
    //     htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    // }, false);

    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);

        //tablo oluştuğunda loading spinner'ını kapatır
        $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
        });

        //sıra numaralarını ekler
        // let i = 1;
        // table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
        //     this.data(i++);
        // });

    });

    //////////////////Tabloya Özel/////////////////
    //Tıklanan hücrede edit yapılmasını sağlar.
    table.DataTable().on( 'click', 'tbody td.editable', function (e) {
        
        editor.inline(this, {
            onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
        });

        $('.DTE_Field input[type="text"]').attr('autocomplete', 'off');

        let thisColumn = table.DataTable().cell(this).index().column;
        editor.on('submitSuccess', function (e, json, data) {
            if(thisColumn == 1){
              $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("show", {
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
                  $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("hide", {
                    animation: "fade"
                  });
              });
            };
        });
    });
  
    //yeni satır ekleme event'i
    table.DataTable().on('click', 'tbody td.row-edit', function (e) {
        editor.inline(table.DataTable().cells(this.parentNode, '*').nodes(), {
            submitTrigger: 1,
            submitHtml: '<i class="fa fa-play"/>',
            onBlur: 'submit'
        });
    });
    //virgül ile girilen ondalık sayıları noktaya çevririr
    editor.on( 'preSubmit', function ( e, json, data, label ) {
        function bul(obj, key) {
            for (var key in obj) {
              if (typeof obj[key] === "object") {
                var outcome = bul(obj[key], key);
                if (outcome !== undefined) {
                  return outcome;
                }
              } else if (key === searchKey) {
                return obj[key];
              }
            }
        };
        function degistir(obj, key, newValue) {
            for (var key in obj) {
              if (typeof obj[key] === "object") {
                degistir(obj[key], key, newValue);
              } else if (key === searchKey) {
                obj[key] = newValue;
              }
            }
        };

        var searchKey = "quantity";
        var outcome = bul(json, searchKey);

        if(outcome !== undefined){
            var newValue = outcome.replace(",",".");
            degistir(json, searchKey, newValue);
        };

        var searchKey = "unitPrice";
        var outcome = bul(json, searchKey);

        if(outcome !== undefined){
            var newValue = outcome.replace(",",".");
            degistir(json, searchKey, newValue);
        };

        var searchKey = "totalPrice";
        var outcome = bul(json, searchKey);

        if(outcome !== undefined){
            var newValue = outcome.replace(",",".");
            degistir(json, searchKey, newValue);
        };
    });

    

    //pdf'i ve total'i günceller
    // editor.on( 'submitSuccess', function ( e, json, data, label ) {
    //     let ee = elementTag;
    //     let efSub = elementTagSub;
    //     let ei = inquiryId;
    //     let cc = inquiryCurrency;
    //     htmx.ajax("POST", "/sale/inquiry_pdf_make/" + inquiryId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
    //     htmx.on("htmx:afterOnLoad", (e) => {
    //         if (e.detail.xhr.status === 204) {
    //             $.ajax({
    //                 url: '/sale/api/inquiries',
    //                 data: {'id': inquiryId},
    //                 dataType: 'json',
    //                 success: function(data) {
    //                     console.log(data);
    //                     $.each(data, function(i, inquiry) {
    //                         console.log(inquiry.totalTotalPrice);
    //                         $("#totalFinalInquiry-" + efSub + "-" + ei + "").val(cc + " " + inquiry.totalTotalPrice.toFixed(2));
    //                     });
    //                 }
    //             });
    //         }
    //     });
    //     $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
    //     // Mesajı belirli bir süre sonra gizle
    //     setTimeout(function() {
    //         $("#message-container-inside-" + ee + "-" + ei).fadeOut("slow");
    //     }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
    // });

    //seçili satırın quantity değerini tüm satırlara kopyalar
    $(".duplicateSelectedQuantityInquiry").on("click", function(){
        if(table.DataTable().row({selected:true}).data()["id"]){
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
          let inquiryPartId = table.DataTable().row({selected:true}).data()["id"];
          htmx.ajax("POST", "/sale/inquiry_part_quantity_duplicate/" + inquiryPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});

        };
        
    });


    //seçili satırın availability değerini tüm satırlara kopyalar
    $(".duplicateSelectedAvailabilityInquiry").on("click", function(){
        if(table.DataTable().row({selected:true}).data()["id"]){
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
          let inquiryPartId = table.DataTable().row({selected:true}).data()["id"];
          htmx.ajax("POST", "/sale/inquiry_part_availability_duplicate/" + inquiryPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
          
        };
        
    });

    //////////////////Tabloya Özel-end/////////////////

    //////////////////Tabloya Özel/////////////////
    //select all işlemi event'i
    $('#select-all-' + es).on( "click", function(e) {
        if ($(this).is( ":checked" )) {
            table.DataTable().rows().select();        
        } else {
            table.DataTable().rows().deselect(); 
        }
    });
  
    //arrow key'ler ile hücrelerde gezinmeyi sağlar
    $(document).on('keyup', function ( e ) {
    if (e.keyCode === 40) { //key down
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.parent().next().children().eq(cellIndex).click();
    }else if(e.keyCode === 38){ //key up
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.parent().prev().children().eq(cellIndex).click();
    }else if(e.keyCode === 37){ //key left
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.prev().click();
    }else if(e.keyCode === 39){ //key right
        e.preventDefault();
        // Find the cell that is currently being edited
        var cell = $('div.DTE').parent();
        var cellIndex = cell.index();
        // Down to the next row
        cell.next().click();
    }
    } );
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
            setTimeout(function(){
                table.DataTable().ajax.reload(function() {
                    htmx.process(tableId);
                }, false);
            },500);
            
            console.log(idList);
        });
    };

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

    ///////////////////////////tabloya özel///////////////////////////
    // table.on('click', 'td', function () {
    //     if(table.DataTable().row(this).data()["partDetails"]["group"]){$("#partGroupInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["group"]);}else{$("#partGroupInfoInput-" + es).text("-");};
    //     if(table.DataTable().row(this).data()["partDetails"]["manufacturer"]){$("#partManufacturerInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["manufacturer"]);}else{$("#partManufacturerInfoInput-" + es).text("-");};
    //     if(table.DataTable().row(this).data()["partDetails"]["crossRef"]){$("#partCrossRefInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["crossRef"]);}else{$("#partCrossRefInfoInput-" + es).text("-");};
    //     if(table.DataTable().row(this).data()["partDetails"]["ourRef"]){$("#partOurRefInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["ourRef"]);}else{$("#partOurRefInfoInput-" + es).text("-");};
    //     if(table.DataTable().row(this).data()["partDetails"]["quantity"]){$("#partQuantityInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["quantity"]);}else{$("#partQuantityInfoInput-" + es).text("-");};
    //     if(table.DataTable().row(this).data()["partDetails"]["lastParts"][0]){
    //         $("#partlast3SalesInfoInput-1-" + es).text(
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["date"] + " | " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["inquiry"] + " | " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["currency"] + " " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["unitPrice"].toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    //         );
    //     }else{
    //         $("#partlast3SalesInfoInput-1-" + es).text("-");
    //     };
    //     if(table.DataTable().row(this).data()["partDetails"]["lastParts"][1]){
    //         $("#partlast3SalesInfoInput-2-" + es).text(
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["date"] + " | " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["inquiry"] + " | " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["currency"] + " " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["unitPrice"].toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    //         );
    //     }else{
    //         $("#partlast3SalesInfoInput-2-" + es).text("-");
    //     };
    //     if(table.DataTable().row(this).data()["partDetails"]["lastParts"][2]){
    //         $("#partlast3SalesInfoInput-3-" + es).text(
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["date"] + " | " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["inquiry"] + " | " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["currency"] + " " +
    //             table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["unitPrice"].toLocaleString('tr-TR', { minimumFractionDigits: 2 })
    //         );
    //     }else{
    //         $("#partlast3SalesInfoInput-3-" + es).text("-");
    //     };
    
    // });


    /////////////////////////tabloya özel-end/////////////////////////
    




    
};

function setNavTabSubPurchasingInquiry(){
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

function formSubmitMessagePurchasingInquiry(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl;
    $("#form-" + ee +  "-" + ei).submit(function (event) {
      event.preventDefault();

      console.log("okey1");
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
                console.log("#message-container-" + ee + "-" + ei);
                $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                console.log("eburasıu");
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

function setHTMXPurchasingInquiry(){
    let ee = elementTag;
    let ei = elementTagId;
    let es = elementTagSub + "-" + elementTagId;
  
    let tableBox = $(".tableBox-" + ee);
    let tableId = "#table-" + ee;
    let table = $("#table-" + ee);
  
    //open
    htmx.on("htmx:afterSwap", (e) => {
        if(e.detail.target.id == "tabContSub-" + ee){
            $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("show", {
                animation: false,
                spinner: "pulsar",
                maxSize: "150px",
                minSize: "150px",
                text: "Loading ...",
                background: "rgba(69, 83, 89, 0.6)",
                color: "#455359",
                textColor: "#fff"
            });
            $(tableId).DataTable().ajax.reload(function(){
                htmx.process(tableId);
            },false);
            table.on( 'draw.dt', function () {
                htmx.process(tableId);
                $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
                    animation: "fade"
                });
            });
        };
        if(e.detail.target.id == "addFormBlock-inform-d-justDetail-" + es){
            $("#table-" + es).DataTable().ajax.reload(function(){
                htmx.process("#table-" + es);
            },false);
            
        };
    });
    //submitted
    htmx.on("htmx:beforeSwap", (e) => {
        let addFormBlockSubID = "tabContSub-" + ee;
        if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
                e.detail.shouldSwap = false;
            $(tableId).DataTable().ajax.reload(function(){
                htmx.process(tableId);
            },false);
        };
        if (e.detail.target.id == "addFormBlock-inform-d-justDetail-" + es && !e.detail.xhr.response) {
            e.detail.shouldSwap = false;
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
            $("#table-" + es).DataTable().ajax.reload(function(){
                htmx.process("#table-" + es);
            },false);
            $("#table-" + es).DataTable().on( 'draw.dt', function () {
                htmx.process("#table-" + es);
                $("body").busyLoad("hide", {
                    animation: "fade"
                });
            });
            history.pushState({}, null, detailRefererPathSub);
        };
        // if (e.detail.target.id == addFormBlockSubID && !e.detail.xhr.response) {
        //     // Başarılı yanıt geldiğinde mesajı görüntüleyin
        //     if (e.detail.xhr.status === 204) {
        //         console.log("#message-container-" + ee + "-" + ei);
        //         $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
        //         // Mesajı belirli bir süre sonra gizle
        //         console.log("eburasıu");
        //         setTimeout(function() {
        //           $("#message-container-inside-" + ee + "-" + ei).fadeOut("slow");
        //         }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
        //     };
        // };
    });
    //cancelled
    htmx.on("hidden.bs.modal", (e) => {
        if (e.target.id == "addFormBlock-inform-d-justDetail-" + es) {
            document.getElementById("addFormBlock-inform-d-justDetail-" + es).innerHTML = "";
        };
    });
  
};

$(document).ready(function () {
    setPurchasingInquiryItemDetailDatatable();
    //setHTMXPurchasingInquiry();
    setNavTabSubPurchasingInquiry();
    formSubmitMessagePurchasingInquiry();
    
});
function setPersonDetailInCompanyDatatable(){
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
/**/let addDataHxGet = "/card/person_add_in_detail_company/";
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
            // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            className: "deleteData tableTopButtons inTableButtons delete-" + es + "",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"},
        },
        {
            // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
            className: "tableTopButtons inTableButtons",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/sync.svg"},
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
/**/let apiSource = '/card/api/persons?company=' + companyId + '&format=datatables';
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


    
};

function setBankDetailInCompanyDatatable(){
    let es = elementTagSub + "-" + elementTagId + "-bank";
    let id = companyId
    
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
/**/let addDataHxGet = "/card/bank_add_in_detail_company/c_" + id + "/";
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
            // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
            className: "deleteData tableTopButtons inTableButtons delete-" + es + "",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/deletefile.svg"}
        },
        {
            // text: '<i class="fa-solid fa-rotate" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Refresh Table"></i>',
            className: "tableTopButtons inTableButtons",
            tag: "img",
            attr: {src:"/static/images/icons/datatable/sync.svg"},
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
/**/let deleteDataUrl = "/card/bank_delete/";
    let serverSide = false;
/**/let apiSource = '/card/api/banks?company=' + companyId + '&format=datatables';
/**/let columns = [
                    {"data" : "id"},
                    {"data" : "bankName", render: function (data, type, row, meta)
                                    {return '<a hx-get="/card/bank_update_in_company/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                                },  
                    {"data" : "accountNo"},
                    {"data" : "ibanNo"},
                    {"data" : "swiftNo"},
                    {"data" : "branchName"},
                    {"data" : "branchCode"},
                    {"data" : "currency"}
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
    
    //sütun gizleme
    table.DataTable().column(0).visible(false);

    //new $.fn.dataTable.FixedHeader( table );

    //tablo her yüklendiğinde oluşan eylemler.
    table.DataTable().ajax.reload(function() {
        htmx.process(tableId); //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    }, false);

    //tablo her çizildiğinde oluşan eylemler
    table.on( 'draw.dt', function () {
        htmx.process(tableId);

        //tablo oluştuğunda loading spinner'ını kapatır
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


    
};

function formSubmitMessageCompany(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl;
  
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

function mikroStatus(){
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
      + cariKod
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


function setNavTabSubCompany(){
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



$(document).ready(function () {
    setPersonDetailInCompanyDatatable();
    setBankDetailInCompanyDatatable();
    setHTMX();
    setNavTabSubCompany();
    //formSubmitMessageCompany();
    //mikroStatus();

    // wsMain.send(JSON.stringify({
    //     "type": "check_mikro",
    //     "location" : "check_mikro_connection",
    //     "cari_kod" : cariKod,
    //     "mikroDBName" : mikroDBName,
    // }));
    
});


        
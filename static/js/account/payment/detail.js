function setPaymenInvoiceDetailDatatable(){
  let es = elementTagSub + "-" + elementTagId;
  let id = paymentId

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
/**/let addDataHxGet = "/account/payment_invoice_add_in_detail/p_" + id + "/";
  //let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
  let addDataHxTarget = "#addUpdateDataDialogXl";
  
  let order = [[1, 'asc']];

  //////////////////Tabloya Özel/////////////////
  //Datatable Editor için editor'ü tanımlar.
  let editor = new $.fn.dataTable.Editor({
    ajax: `/account/api/payment_invoices/editor/`,
    table: tableId,
    idSrc: "id",
    fields: [
      {
        label: "amount",
        name: "amount",
      }
    ]
  });



  
  //////////////////Tabloya Özel-end/////////////////

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
          text: 'data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"',
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
          }
      },
      {
        // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
        tag: "img",
        attr: {src:"/static/images/icons/datatable/budgeting.svg"}, 
        className: "tableTopButtons inTableButtons",
        action: function ( e, dt, node, config ) {
            htmx.ajax('POST', `/account/payment_invoice_amount/p_${paymentId}/`, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        }
       }
  ];

  let addToInquiryDataButtonId = ".addToInquiryData";

  let deleteDataButton = $('.deleteData');
  let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/account/payment_invoice_delete/";
  let serverSide = false;
/**/let apiSource = `/account/api/payment_invoices?payment=${paymentId}&format=datatables`;
/**/let columns = [
      {
          orderable: false,
          searchable: false,
          className: 'select-checkbox',
          targets: 0,
          "width": "1%"
      },
      {"data" : "", className : "editable"},
      {"data" : "id","visible":false},
      {"data" : "project", "width": "10%", className:"text-start ps-1 pe-1"},
      {"data" : "invoice", "width": "14%", className:"text-start ps-1 pe-1"},
      {"data" : "invoiceDate", className:"text-center ps-1 pe-1", "width": "10%"},
      {"data" : "invoicePaymentDate","width" : "10%", className:"editable text-center ps-1 pe-1", orderable: false},
      {"data" : "invoiceTotalPrice", className:"text-end ps-1 pe-1", "width": "10%", render: function (data, type, row, meta){
        return '<span class="">' + data.toLocaleString('tr-TR', {  minimumFractionDigits: 2 }) + '</span>';
      }
      },
      {"data" : "invoiceBalance", className:"text-end ps-1 pe-1", "width": "10%", render: function (data, type, row, meta){
        return '<span class="">' + data.toLocaleString('tr-TR', {  minimumFractionDigits: 2 }) + '</span>';
      }
      },
      {"data" : "invoiceCurrencyAmount", className:"text-end ps-1 pe-1", "width": "10%", render: function (data, type, row, meta){
        return '<span class="">' + data.toLocaleString('tr-TR', {  minimumFractionDigits: 2 }) + '</span>';
      }
      },
      {"data" : "invoiceCurrency", "width": "5%", className:"text-center ps-1 pe-1"},
      {"data" : "amount", className:"editable text-end ps-1 pe-1", "width": "15%", render: function (data, type, row, meta){
        return '<span class="">' + data.toLocaleString('tr-TR', {  minimumFractionDigits: 2 }) + '</span>';
      }
      }
  ];

  table.DataTable({
      order : order,
      "serverSide" : serverSide,
      "processing" : true,
      "autoWidth": false,
      select: {
        style: 'single',
        selector: 'td:first-child'
      },
      //"pageLength": 20,
      paging: false,
      scrollY : "40vh",
      scrollX : true,
      scrollCollapse: true,
      //rowReorder: true,
      // rowReorder: {
      //   dataSrc: 'sequency',
      //   editor: editor,
      //   selector: 'td:nth-child(2)'
      // },
      rowReorder : false,
      fixedHeader: {
        header: true,
        headerOffset: $('#fixed').height()
      },
      responsive : true,
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
          
          // for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
          //   $(tableId + ' tbody').append($("<tr ></tr>"));
          // }
      },
      "ajax" : apiSource,
      "columns" : columns
    });
  
  //sütun gizleme
  //table.DataTable().column(2).visible(false);

  //new $.fn.dataTable.FixedHeader(table);
  
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

      // sıra numaralarını ekler
      let i = 1;
      table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

  });

  
  //////////////////Tabloya Özel/////////////////
  //Tıklanan hücrede edit yapılmasını sağlar.
  table.DataTable().on( 'click', 'tbody td.editable', function (e) {
    // editor.edit(table.DataTable().cell(this).index(), {
    //   focus: null
    // });
    editor.inline(table.DataTable().cell(this).index(), {
        onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
    });

    $('.DTE_Field input[type="text"]').attr('autocomplete', 'off');

    
    
    // editor.on('processing', function (e, json, data) {
    //     if(!$(".successSpin").length){
    //         $(".tableBox-inform-" + es + " .dt-buttons").append('<button type="button" class="dt-button tableTopButtons inTableButtons successSpin"><i class="fa-solid fa-gear fa-spin"></i></button>');
    //     };
        
    // });
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
        

        // setTimeout(function() {
        //     $(".successSpin").remove();
        // }, 1000);
        
    });
} );

  
  //////////////////Tabloya Özel-end/////////////////

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

    var searchKey = "amount";
    var outcome = bul(json, searchKey);

    if(outcome !== undefined){
        var newValue = outcome.replace(",",".");
        degistir(json, searchKey, newValue);
    };
});

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
        //işlemler
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
            $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
              animation: "fade"
            });
        },1000);
        
        
      });
  };

  // default loading spinner'ı gizler
  $("div.dataTables_processing").remove();
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});


  
};

function formSubmitMessagePayment(){
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

function setHTMXPayment(){
    let ee = elementTag;
    let ei = elementTagId;
  
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
        // $(tableId).DataTable().ajax.reload(function(){
        //   htmx.process(tableId);
        // },false);
        table.on( 'draw.dt', function () {
          htmx.process(tableId);
          $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
            animation: "fade"
          });
        });
      };
    });
    //submitted
    htmx.on("htmx:beforeSwap", (e) => {
      if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
        e.detail.shouldSwap = false;
        $(tableId).DataTable().ajax.reload(function(){
          htmx.process(tableId);
        },false);
      };
    });
    //cancelled
    htmx.on("hidden.bs.modal", (e) => {
      
    });
  
};

function setNavTabSubPayment(){
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

function select2Payment(){
  $('#formOutline-payment-customer').select2({
      ajax: {
        url: "/account/payment_add/",
        dataType: 'json',
        delay: 250,
        data: function (params) {
          return {
            term: params.term,  // Arama terimi
            type: 'company'    // Hangi select2 için olduğunu belirtmek için 'type' parametresi
          };
        },
        escapeMarkup: function (markup) { return markup; },
        processResults: function (data) {
          return {
          results: $.map(data, function (item) {
              // tek satırda koşul sorgulamak için; sorgu ? koşul sağlanıyorsa değer : koşul sağlanmıyorsa değer
              text = `
                  <span>${item.name}</span>
              `
              return {id: item.id,
                      name: item.name ? item.name : "---"
                  };
            })
          };
        }
      },
      escapeMarkup: function (markup) { return markup; }, // HTML işleme için escape yapmıyoruz
      templateResult: function (data) {
          if (!data.id) { 
              return data.text;
          }

          // Burada özel HTML şablonunu oluşturun
          var markup = `
              <span>${data.name}</span>
          `;
          return markup;
          },
          templateSelection: function (data) {
            if(data.id){
              var markup = `${data.text}`;
            }else{
              var markup = "Search for a company";
            };
            
            return markup;
      },
      minimumInputLength: 3,
      placeholder: "Search for a company",
      allowClear: true,
      closeOnSelect: true,
      minimumResultsForSearch: Infinity,
      scrollAfterSelect: true,
      width: "100%",
      dropdownCssClass: "paymentSelect2"
  });


  $(".paymentSelect2 .select2-results__option.select2-results__option--selectable").css({"font-size":"6px"});


  $(`#formOutline-payment-sourceBank-${elementTagId}`).select2({
    ajax: {
      url: "/account/payment_add/",
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return {
          term: params.term,  // Arama terimi
          type: 'bank'    // Hangi select2 için olduğunu belirtmek için 'type' parametresi
        };
      },
      escapeMarkup: function (markup) { return markup; },
      processResults: function (data) {
        return {
          results: $.map(data, function (item) {
              // tek satırda koşul sorgulamak için; sorgu ? koşul sağlanıyorsa değer : koşul sağlanmıyorsa değer
              text = `
                  <span>${item.bankName}</span>
              `
              return {id: item.id,
                      bankName: item.bankName ? item.bankName : "---",
                      ibanNo: item.ibanNo ? item.ibanNo : "---",
                      currency: item.currency__code ? item.currency__code : "---"
                  };
          })
        };
      }
    },
    escapeMarkup: function (markup) { return markup; }, // HTML işleme için escape yapmıyoruz
    templateResult: function (data) {
        if (!data.id) { 
            return data.text;
        }

        // Burada özel HTML şablonunu oluşturun
        var markup = `
            <div class='p-0 m-0 border-bottom'>
                    <table class="no-footer p-0 m-0" style="width:100%;">
                        <thead>
                            <tr>
                                <td style="width:50%; font-weight:bold;">Bank Account</td>
                                <td style="width:40%; font-weight:bold;">IBAN</td>
                                <td style="width:10%; font-weight:bold;">Currency</td>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>${data.bankName}</td>
                                <td>${data.ibanNo}</td>
                                <td>${data.currency}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
        `;
        return markup;
    },
    templateSelection: function (data) {
        if(data.id){
          var markup = `${data.text}`;
        }else{
          var markup = "Search for a bank";
        };
        
        return markup;
    },
    //minimumInputLength: 3,
    placeholder: "Search for a bank",
    allowClear: true,
    closeOnSelect: true,
    minimumResultsForSearch: 1,
    scrollAfterSelect: true,
    width: "100%",
    dropdownCssClass: "bankSelect2"
  });

  $(".bankSelect2 .select2-results").css({"max-height":"600px"});
  $(".bankSelect2 .select2-results__option.select2-results__option--selectable").css({"font-size":"6px"});
  
};

$(document).ready(function () {
    setPaymenInvoiceDetailDatatable();
    setHTMXPayment();
    setNavTabSubPayment();
    //formSubmitMessagePayment();
    select2Payment();
    
});
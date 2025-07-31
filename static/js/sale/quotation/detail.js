function setQuotationPartDetailDatatable(){
    let es = elementTagSub + "-" + elementTagId;
    let id = quotationId

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
/**/let addDataHxGet = "/sale/quotation_part_add_in_detail/q_" + id + "/";
    let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;

    let order = [[1, 'asc'],[2, 'asc']];

    //////////////////Tabloya Özel/////////////////
    //Datatable Editor için editor'ü tanımlar.
    if(revised == "True"){
      var qtyBlock = []
    }else if(orderConfirmation == 1){
      var qtyBlock = [
        {
          label: "sequency",
          name: "sequency",
      },{
            label: "profit",
            name: "profit",
        },
        {
          label: "unitPrice2",
          name: "unitPrice2",
        },
        {
          label: "totalPrice2",
          name: "totalPrice2",
        },
        {
            label: "discount",
            name: "discount",
        },
        {
          label: "unitPrice3",
          name: "unitPrice3",
        },
        {
          label: "totalPrice3",
          name: "totalPrice3",
        },
        {
            label: "availabilityChar",
            name: "availabilityChar",
        },
        {
          label: "note",
          name: "note"
        },{
          label: "remark",
          name: "remark",
          type: 'textarea'
        }
    ]
    }else{
      var qtyBlock = [
        {
          label: "sequency",
          name: "sequency",
      },{
          label: "quantity",
          name: "quantity"
        },
        {
            label: "profit",
            name: "profit",
        },
        {
          label: "unitPrice2",
          name: "unitPrice2",
        },
        {
          label: "totalPrice2",
          name: "totalPrice2",
        },
        {
            label: "discount",
            name: "discount",
        },
        {
          label: "unitPrice3",
          name: "unitPrice3",
        },
        {
          label: "totalPrice3",
          name: "totalPrice3",
        },
        {
            label: "availabilityChar",
            name: "availabilityChar",
        },
        {
          label: "note",
          name: "note",
          type: 'textarea'
        },{
          label: "remark",
          name: "remark",
          type: 'textarea'
        }
    ]
    };
    let editor = new $.fn.dataTable.Editor({
      ajax: "/sale/api/quotation_parts/editor/",
      table: tableId,
      idSrc: "id",
      fields: qtyBlock
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
        // {
        //     // text: '<i class="fa-solid fa-trash" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Remove selected rows"></i>',
        //     tag: "img",
        //     attr: {src:"/static/images/icons/datatable/deletefile.svg"},
        //     className: "deleteData tableTopButtons inTableButtons delete-" + es + ""
        // },
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
        }
    ];

    if(revised == "True" || revised == "False"){
      var buttons = [
        {
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
        }
      ]
    };

    if(rev == "True" || revised == "False"){
      var buttons = [
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
        }
      ]
    };

    let deleteDataButton = $('.deleteData');
    let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/sale/quotation_part_delete/";
    let serverSide = false;
/**/let apiSource = '/sale/api/quotation_parts?quotation=' + quotationId + '&format=datatables';
/**/let columns = [
        {
            orderable: false,
            className: 'select-checkbox ps-1 pe-1',
            targets: 0,
            "width": "1%"
        },
        {"data" : "sequency","width": "1%", className:"editable ps-1 pe-1", "visible":true},
        {"data" : "alternative","width": "1%", className:"ps-1 pe-1","visible":false, render: function (data, type, row, meta){
          if(data == true){
            return row.sequency + "-A"
          }else{
            return row.sequency
          };
          
        }
        },
        {"data" : "alternative","width": "1%", className:"ps-1 pe-1","visible":false, render: function (data, type, row, meta){
          if(row.alternative == true){
            return '<input class="form-check-input" type="radio" value="" id="mainCheckPart" name="name-' + row.requestPart + '">';
          }else{
            return '<input class="form-check-input" type="radio" value="" id="mainCheckPart" name="name-' + row.requestPart + '" checked>';
          };
          
          
        }
        },
        {"data" : "id", "visible" : false},
        // {"data" : "inquiryPart.requestPart.part.partNo", render: function (data, type, row, meta)
        //                 {return '<a hx-get="/sale/quotation_part_update/' + row.id + '/" hx-target="#addFormBlock-inform-d-justDetail-' + es + '" hx-push-url="true" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
        // },
        {"data" : "partNo", className:"text-start ps-1 pe-1", "width": "6%"},
        {"data" : "description", className:"text-start ps-1 pe-1", "width": "15%"},
        {"data" : "quantity", className:"editable text-end ps-1 pe-1", "width": "5%"},
        {"data" : "unit", className:" ps-1 pe-1", "width": "1%"},
        {"data" : "unitPrice1", className:"text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice1", className:"text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "profit", className:"editable text-end ps-1 pe-1", orderable: false, "width": "5%", render: function (data, type, row, meta)
                        {return (data).toFixed(2) + " %"}
        },
        {"data" : "unitPrice2", className:"editable text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice2", className:"editable text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "discount", className:"editable text-end ps-1 pe-1", orderable: false, "width": "5%", render: function (data, type, row, meta)
                        {return (data).toFixed(2) + " %"}
        },
        {"data" : "unitPrice3", className:"editable text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "totalPrice3", className:"editable text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                        {return row.currency + " " + (data).toFixed(2)}
        },
        {"data" : "availabilityChar", className:"editable ps-1 pe-1",  orderable: false, "width": "8%", render: function (data, type, row, meta){
                          function isNumeric(str) {
                            return /^\d+$/.test(str);
                          };
                          if(isNumeric(data) == true){
                            if(data > 1){
                              return data + " " + row.availabilityType + "s";
                            }else if(data == 1){
                              return data + " " + row.availabilityType;
                            }else if(data < 1){
                              return data + " " + row.availabilityType;
                            }else{
                              return data + " " + row.availabilityType;
                            };
                          }else if(isNumeric(data) == false){
                            return data;
                          };
        }
        },
        {"data" : "note", className:"editable note ps-1 pe-1", orderable: false, "width": "8%"},
        {"data" : "remark", className:"editable remark ps-1 pe-1", orderable: false, "width": "10%"},
        {"data" : "availabilityType", "visible" : false},
        {"data" : "quotation.currency", "visible" : false},
        {"data" : "requestPart", "visible" : false},
        {"data" : "supplier", className:"ps-1 pe-1", "width": "5%"}
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
        paging : false,
        scrollY : "38vh",
        scrollX : true,
        scrollCollapse: true,
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
        responsive : false,
        language: { search: '', searchPlaceholder: "Search..." },
        dom : 'Bfrtip',
        buttons : buttons,
        fixedHeader : {
          header: false,
          footer: false
        },
        columnDefs: [{
          "defaultContent": "",
          "targets": "_all"
        }],
        createdRow: function(row, data, index) {

          var alternative = data.alternative;

          if(alternative == true){
            $('td:eq(1)', row).removeClass("reorder")
          };

          $('td:eq(17)', row).css({"cursor" : "pointer"});

          $('td:eq(17)', row).on("click", function(){
            htmx.ajax("GET", "/sale/quotation_part_source?qp=" + data["id"], {target : "#addUpdateDataDialogXl"});
          });

        },
        drawCallback: function() {
            var api = this.api();
            var rowCount = api.rows({page: 'current'}).count();

            let totalQuantity = 0

            for (var i = 0; i < api.page.len() - (rowCount === 0? 1 : rowCount); i++) {
              $(tableId + ' tbody').append($("<tr ></tr>"));
            }
        },
        // createdRow: function(row, data, index) {
        //   $('td:eq(8)', row).css('background-color', '#C8E6C9');
        //   $('td:eq(11)', row).css('background-color', '#FFCCBC');
        // },
        "ajax" : apiSource,
        "columns" : columns
      });

    new $.fn.dataTable.FixedHeader(table);
    
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
            
            $(this).css({"width":"10%"});
            table.on( 'draw.dt', function () {
                htmx.process(tableId);
                $(".tableBox-inform-" + es + " .dataTables_scroll").busyLoad("hide", {
                  animation: "fade"
                });
            });
          };
      });
    });

    //remark area
    editor.on('open', function (e, json, data, mode, action) {
      $("#DTE_Field_remark").parent().parent().parent().parent().parent().parent().css({"width":"200%"});
      table.DataTable().columns.adjust();
    });

    editor.on('preClose', function (e, json, data) {
      $("#DTE_Field_remark").parent().parent().parent().parent().parent().parent().css({"width":"10%"});
      table.DataTable().columns.adjust();
    });

    //Taşıma işlemi.
    table.DataTable().on( 'row-reorder', function (e, diff, edit) {
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
      idList = []
      oldList = []
      newList = []
      rowDataList = []
      for (var i = 0, ien = diff.length; i < ien; i++) {
        let rowData = table.DataTable().row(diff[i].node).data();
        rowDataList.push(rowData);
        //console.log(rowData["theRequest"]["project"]["id"]);
        idList.push(rowData["id"])
        oldList.push(diff[i].oldData)
        newList.push(diff[i].newData)
        //console.log("part: " + rowData["part"]["partNo"] + " old: " + diff[i].oldData + " new: " + diff[i].newData);
        //console.log(rowData["id"]);
        //htmx.ajax("POST", "/sale/request_part_reorder/p_" + rowData["id"] + "_old_" + diff[i].oldData + "_new_" + diff[i].newData + "/", {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
      };
      htmx.ajax("POST", "/sale/quotation_part_reorder/q_" + rowDataList[0]["quotationId"] + "_p_" + idList + "_old_" + oldList + "_new_" + newList, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
      
      htmx.on("htmx:beforeSwap", function(e){
        console.log(e.detail);
        if (e.detail.target.id == "addUpdateDataDialog-inform" && !e.detail.xhr.response){
          if(e.detail.xhr.status == 204){
            table.DataTable().ajax.reload()

            table.on( 'draw.dt', function () {
                htmx.process(tableId);
                $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
                  animation: "fade"
                });
            });
          };
        };
      });

      // setTimeout(function() {
      //   table.DataTable().ajax.reload()

      //   table.on( 'draw.dt', function () {
      //       htmx.process(tableId);
      //       $(".tableBox-inform-" + es + " .dataTables_scrollBody").busyLoad("hide", {
      //         animation: "fade"
      //       });
      //   });
      // },1500);
    
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

      var searchKey = "profit";
      var outcome = bul(json, searchKey);
      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };

      var searchKey = "unitPrice2";
      var outcome = bul(json, searchKey);
      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };

      var searchKey = "totalPrice2";
      var outcome = bul(json, searchKey);
      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };

      var searchKey = "discount";
      var outcome = bul(json, searchKey);
      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };

      var searchKey = "unitPrice3";
      var outcome = bul(json, searchKey);
      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };

      var searchKey = "totalPrice3";
      var outcome = bul(json, searchKey);
      if(outcome !== undefined){
          var newValue = outcome.replace(",",".");
          degistir(json, searchKey, newValue);
      };
    });

    //seçili satırın profit değerini tüm satırlara kopyalar
    $(".duplicateSelectedProfitQuotation").on("click", function(){
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
        let quotationPartId = table.DataTable().row({selected:true}).data()["id"];
        htmx.ajax("POST", "/sale/quotation_part_profit_duplicate/" + quotationPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        
        setTimeout(function() {
          table.DataTable().ajax.reload()
  
          table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          });
        },1500);
      };
      
    });

    //seçili satırın discount değerini tüm satırlara kopyalar
    $(".duplicateSelectedDiscountQuotation").on("click", function(){
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
        let quotationPartId = table.DataTable().row({selected:true}).data()["id"];
        htmx.ajax("POST", "/sale/quotation_part_discount_duplicate/" + quotationPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        
        setTimeout(function() {
          table.DataTable().ajax.reload()
  
          table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          });
        },1500);
      };
      
    });

    //seçili satırın availability değerini tüm satırlara kopyalar
    $(".duplicateSelectedAvailabilityQuotation").on("click", function(){
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
        let quotationPartId = table.DataTable().row({selected:true}).data()["id"];
        htmx.ajax("POST", "/sale/quotation_part_availability_duplicate/" + quotationPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        
        setTimeout(function() {
          table.DataTable().ajax.reload()
  
          table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          });
        },1500);
      };
      
    });

    //seçili satırın note değerini tüm satırlara kopyalar
    $(".duplicateSelectedNoteQuotation").on("click", function(){
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
        let quotationPartId = table.DataTable().row({selected:true}).data()["id"];
        htmx.ajax("POST", "/sale/quotation_part_note_duplicate/" + quotationPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        
        setTimeout(function() {
          table.DataTable().ajax.reload()
  
          table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          });
        },1500);
      };
      
    });

    //seçili satırın remark değerini tüm satırlara kopyalar
    $(".duplicateSelectedRemarkQuotation").on("click", function(){
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
        let quotationPartId = table.DataTable().row({selected:true}).data()["id"];
        htmx.ajax("POST", "/sale/quotation_part_remark_duplicate/" + quotationPartId, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
        
        setTimeout(function() {
          table.DataTable().ajax.reload()
  
          table.on( 'draw.dt', function () {
              htmx.process(tableId);
              $(".tableBox-inform-" + elementTagSub + "-" + elementTagId + " .dataTables_scrollBody").busyLoad("hide", {
                animation: "fade"
              });
          });
        },1500);
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

        });
    };

    // default loading spinner'ı gizler
    $("div.dataTables_processing div").hide();
    $("div.dataTables_processing").css({"box-shadow":"none"});

    ///////////////////////////tabloya özel///////////////////////////
    table.on('click', 'td', function () {
      console.log(table.DataTable().row(this).data()["partDetails"]);
      if(table.DataTable().row(this).data()["partDetails"]["group"]){$("#partGroupInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["group"]);}else{$("#partGroupInfoInput-" + es).text("-");};
      if(table.DataTable().row(this).data()["partDetails"]["manufacturer"]){$("#partManufacturerInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["manufacturer"]);}else{$("#partManufacturerInfoInput-" + es).text("-");};
      if(table.DataTable().row(this).data()["partDetails"]["crossRef"]){$("#partCrossRefInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["crossRef"]);}else{$("#partCrossRefInfoInput-" + es).text("-");};
      if(table.DataTable().row(this).data()["partDetails"]["ourRef"]){$("#partOurRefInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["ourRef"]);}else{$("#partOurRefInfoInput-" + es).text("-");};
      if(table.DataTable().row(this).data()["partDetails"]["quantity"]){$("#partQuantityInfoInput-" + es).text(table.DataTable().row(this).data()["partDetails"]["quantity"]);}else{$("#partQuantityInfoInput-" + es).text("-");};
      if(table.DataTable().row(this).data()["partDetails"]["lastParts"][0]){
          $("#partlast3SalesInfoInput-1-" + es).text(
              table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["date"] + " | " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["project"] + " | " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["currency"] + " " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][0]["unitPrice3"].toLocaleString('tr-TR', { minimumFractionDigits: 2 })
          );
      }else{
        $("#partlast3SalesInfoInput-1-" + es).text("-");
      };
      if(table.DataTable().row(this).data()["partDetails"]["lastParts"][1]){
          $("#partlast3SalesInfoInput-2-" + es).text(
              table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["date"] + " | " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["project"] + " | " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["currency"] + " " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][1]["unitPrice3"].toLocaleString('tr-TR', { minimumFractionDigits: 2 })
          );
      }else{
        $("#partlast3SalesInfoInput-2-" + es).text("-");
      };
      if(table.DataTable().row(this).data()["partDetails"]["lastParts"][2]){
          $("#partlast3SalesInfoInput-3-" + es).text(
              table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["date"] + " | " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["project"] + " | " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["currency"] + " " +
              table.DataTable().row(this).data()["partDetails"]["lastParts"][2]["unitPrice3"].toLocaleString('tr-TR', { minimumFractionDigits: 2 })
          );
      }else{
        $("#partlast3SalesInfoInput-3-" + es).text("-");
      };
    });

    
    /////////////////////////tabloya özel-end/////////////////////////




    
};

function setQuotationExtraDetailDatatable(){
  let es = elementTagSub + "-" + elementTagId + "-extra";
  let id = quotationId

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
/**/let addDataHxGet = "/sale/quotation_extra_add_in_detail/i_" + id + "/";
  let addDataHxTarget = "#addFormBlock-inform-d-justDetail-" + es;
  
  let order = [[1, 'asc']];

  //////////////////Tabloya Özel/////////////////
  //Datatable Editor için editor'ü tanımlar.
  let editor = new $.fn.dataTable.Editor({
      ajax: "/sale/api/quotation_extras/editor/",
      table: tableId,
      idSrc: "id",
      fields: [{
          label: "description",
          name: "description",
      },{
        label: "quantity",
        name: "quantity",
      },{
        label: "unitPrice",
        name: "unitPrice",
      },{
        label: "totalPrice",
        name: "totalPrice",
      }]
  });
  //////////////////Tabloya Özel-end/////////////////

  var buttons = [
      {
      // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
      tag: "img",
      attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
      className: "tableTopButtons inTableButtons",
      action: function ( e, dt, node, config ) {
          htmx.ajax('GET', addDataHxGet, addDataHxTarget);
      }
      },
      // {   
      //     // text: '<i class="fa-solid fa-plus" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Add a new"></i>',
      //     className: "tableTopButtons inTableButtons",
      //     tag: "img",
      //     attr: {src:"/static/images/icons/datatable/add-file.svg"}, 
      //     extend: 'createInline',
      //     editor,
      //     formOptions: {
      //         submitTrigger: 1,
      //         submitHtml: '<i class="fa fa-play"/>',
      //         onBlur: 'submit'
      //     }
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

  //revize kontrol
  if(revised == "True"){
    var buttons = [];
  };

  let deleteDataButton = $('.deleteData');
  let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/sale/quotation_extra_delete/";
  let serverSide = false;
/**/let apiSource = '/sale/api/quotation_extras?quotation=' + quotationId + '&format=datatables';
/**/let columns = [
      {
          orderable: false,
          searchable: false,
          className: 'select-checkbox',
          targets: 0,
          "width": "1%"
      },
      {"data" : "sequency","width": "3%"},
      {"data" : "id"},
      {"data" : "description", className:"editable"},
      {"data" : "quantity", className:"editable text-end ps-1 pe-1", "width": "5%"},
      {"data" : "unitPrice", className:"editable text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      },
      {"data" : "totalPrice", className:"editable text-end ps-1 pe-1", "width": "6%", render: function (data, type, row, meta)
                      {return row.currency + " " + (data).toFixed(2)}
      }
  ];

  table.DataTable({
      order : order,
      "serverSide" : serverSide,
      "processing" : true,
      "autoWidth": true,
      select: {
        style: 'multi',
        selector: 'td:first-child'
      },
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
      columnDefs: [{
          "defaultContent": "",
          "targets": "_all"
        }],
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
  table.DataTable().column(2).visible(false);

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

      //sıra numaralarını ekler
      let i = 1;
      table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
          this.data(i++);
      });

  });

  //////////////////Tabloya Özel/////////////////
  //Tıklanan hücrede edit yapılmasını sağlar.
  table.DataTable().on( 'click', 'tbody td.editable', function (e) {
      console.log(this);
      editor.inline(this, {
          onBlur: 'submit' //hücre dışında herhangi bir yere tıklandığında direkt post işlemi yapar.
      });
  } );

  //yeni satır ekleme event'i
  table.DataTable().on('click', 'tbody td.row-edit', function (e) {
      editor.inline(table.DataTable().cells(this.parentNode, '*').nodes(), {
          submitTrigger: 1,
          submitHtml: '<i class="fa fa-play"/>',
          onBlur: 'submit'
      });
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
  $("div.dataTables_processing").remove();
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});

};

function setNavTabSubQuotation(){
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


function formSubmitMessageQuotation(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
  
    $("#form-quotation-" + ei).submit(function (event) {
      event.preventDefault();
  
      $.ajax({
        type: "POST",
        url: $(this).attr('action'),  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
          console.log(xhr.status);
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
              console.log("#message-container-" + ee + "-" + ei);
                $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                setTimeout(function() {
                  $("#message-container-inside-" + ee + "-" + ei).fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            };
            if (xhr.status === 206) {
              console.log("çüş")
            };;
        },
        error: function (xhr, status, error) {
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
        }
      });
      
    });
  
    $("#form-" + ee +  "-" + ei + "-add-2").submit(function (event) {
      event.preventDefault();
  
      $.ajax({
        type: "POST",
        url: u,  // Formunuzun işleneceği view'ın URL'si
        data: $(this).serialize(),
        success: function (response, status, xhr) {
            // Başarılı yanıt geldiğinde mesajı görüntüleyin
            if (xhr.status === 204) {
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
            
                  let eSub = ee +  "-" + ei + "-add-2";
            
                  let navTagSub = $("#navTag-" + eSub);
                  let tabPaneSub = $("#tabPane-" + eSub);
            
                  navTagSub.prev().children("a").addClass("active");
                  tabPaneSub.prev().addClass("show active");
                  
                  navTagSub.prev().children("a").children("button").show();
                  $("#table-" + ee).DataTable().columns.adjust();
                  
                  navTagSub.remove();
                  tabPaneSub.remove();
            
                  setTimeout(function() {
                    $("body").busyLoad("hide", {
                      animation: "fade"
                    });
                  }, 1000);
            
                }, 2000);
                $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
                // Mesajı belirli bir süre sonra gizle
                console.log("eburasıu");
                setTimeout(function() {
                  $("#message-container-inside-" + ee + '-' + ei + "-add-2").fadeOut("slow");
                }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
            }
        },
        error: function (xhr, status, error) {
            // Hata durumunda mesajı görüntüleyin
            $("#message-container-" + ee + '-' + ei + "-add-2").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-2" + '"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
        }
      });
      
  
      
  
    });
};



$(document).ready(function () {
    setQuotationPartDetailDatatable();
    setQuotationExtraDetailDatatable();
    setNavTabSubQuotation();
    formSubmitMessageQuotation();
    
});
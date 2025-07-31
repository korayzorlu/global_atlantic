var wsMain;
function mainWebSocket(){
  
  wsMain = new WebSocket(
    (window.location.protocol === 'https:' ? 'wss://' : 'ws://')
    + window.location.host
    + '/ws/socket/'
    + user
    + '/'
  );

  wsMain.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const type = data.type
    const message = data.message;
    if(type === "send_notification"){
      send_notification(message);
    }else if(type === "send_percent"){
      send_percent(data);
    }else if(type === "send_alert"){
      send_alert(data);
    }else if(type === "match_mikro_new"){
      match_mikro_new(data);
    }else if(type === "update_mikro"){
      update_mikro(data);
    }else if(type === "create_mikro"){
      create_mikro(data);
    }else if(type === "send_process"){
      send_process(data);
    }else if(type === "update_detail"){
      update_detail(data);
    }else if(type === "reload_table"){
      reload_table(data);
    }else if(type === "reload_micho"){
      reload_micho(data);
    }

  };
  

  wsMain.onopen = function() {
      console.log('WebSocket bağlantısı başarıyla kuruldu.');
  };
  wsMain.onerror = function(error) {
      console.error('WebSocket hatası:', error);
      wsMain.close();
  };

  wsMain.onclose = function () {
    console.log("Websocket kapatıldı!");
    setTimeout(function() {
      mainWebSocket();
    }, 1000);
  };

  window.onload = function() {
    wsMain.close();
  };

  window.onbeforeunload = function() {
      wsMain.close();
  };
};

function send_notification(message){
  if(message === "deleted"){
    // getting object of count
    count = document.getElementById('bellNotify').getAttribute('data-count');
    document.getElementById('bellNotify').setAttribute('data-count', parseInt(count) - 1);
    newCount = parseInt(count) - 1;
    document.getElementById('bellNotify').innerText = newCount;

    $("#notifyTitle").next().remove();
  }else{
    
    // Call the setMessage function to add the new li element
    // Create a new li element
    var newLi = document.createElement('li');

    // Create a new anchor element
    var newAnchor = document.createElement('a');
    newAnchor.className = 'dropdown-item text-wrap';
    newAnchor.href = '#';
    newAnchor.textContent = message;

    // Append the anchor element to the li element
    newLi.appendChild(newAnchor);

    var noNotifyText = document.getElementById('noNotifyText');
    if(noNotifyText){
        noNotifyText.remove()
    };

    var notifyTitle = document.getElementById('notifyTitle');

    // Get the ul element with the id "notify"
    var ulElement = document.getElementById('notify');

    // Append the new li element to the ul element
    //ulElement.prepend(newLi);

    notifyTitle.parentNode.insertBefore(newLi, notifyTitle.nextSibling);

    // getting object of count
    count = document.getElementById('bellNotify').getAttribute('data-count');
    document.getElementById('bellNotify').setAttribute('data-count', parseInt(count) + 1);
    newCount = parseInt(count) + 1;
    document.getElementById('bellNotify').innerText = newCount;

    

    // var totalCount = 24000
    // var singleCount = count
    // var percentCount = singleCount/(totalCount/100)

    // $("#testProgressBar").css({"width":percentCount + "%"});

  };
};

function send_alert(data){
  if(data.location == "form"){
    if(data.message.stage == "loading"){
      document.getElementById(data.message.block).innerHTML = `<i class="fas fa-${data.message.icon} me-3 loading-icon"></i>${data.message.message}`;
      $(`#${data.message.buttons}`).attr("disabled","true");
    }else if(data.message.stage == "completed"){
      document.getElementById(data.message.block).innerHTML = `<i class="fas fa-${data.message.icon} me-3"></i>${data.message.message}`;
      $(`#${data.message.buttons}`).removeAttr("disabled");
      setTimeout(function() {
        $(`#${data.message.block}`).fadeOut("slow", function() {
          document.getElementById(data.message.block).innerHTML = '';
          $(`#${data.message.block}`).fadeIn();
        });
      }, 2000);
    }else{
      document.getElementById(data.message.block).innerHTML = `<i class="fas fa-${data.message.icon} me-3"></i>${data.message.message}`;
      setTimeout(function() {
        $(`#${data.message.block}`).fadeOut("slow", function() {
          document.getElementById(data.message.block).innerHTML = '';
          $(`#${data.message.block}`).fadeIn();
        });
      }, 2000);
    };
    
  }else{
    if(data.location == "default"){
      mainTopAlert.update({color:data.message.status});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-'+data.message.icon+' me-3"></i>' + data.message.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    }else if(data.location == "check_mikro_connection"){
      mainTopAlert.update({color:data.message.status});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-'+data.message.icon+' me-3"></i>' + data.message.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    }else if(data.location == "match_mikro"){
      mainTopAlert.update({color:data.message.status});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-'+data.message.icon+' me-3"></i>' + data.message.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
      reload_tab(data.message.variable);
    }else if(data.location == "unmatch_mikro"){
      mainTopAlert.update({color:data.message.status});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-'+data.message.icon+' me-3"></i>' + data.message.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
      reload_tab(data.message.variable);
    }else if(data.location == "create_mikro"){
      mainTopAlert.update({color:data.message.status});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-'+data.message.icon+' me-3"></i>' + data.message.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
      reload_tab(data.message.variable);
    }
  
    $("#mainTopAlertClose").on("click", function(){
      mainTopAlert.hide();
    });
  
    //spinner durdurur
    $("body").busyLoad("hide", {
        animation: "fade"
    });
  
    mainTopAlert.show();
  };
  
    
};

function match_mikro_new(data){
  if(data.location == "match_mikro_company"){
    console.log(data);
    if(data.status == "success"){
      let matchedCompanyId = data.data.companyId;
      $("#matchMikroLoader-companyPartInMatchWith-"+matchedCompanyId).busyLoad("hide", {
        animation: "fade"
      });
      $("#matchMikroLoaderBlock-companyPartInMatchWith-"+matchedCompanyId).addClass("d-none");
      $("#matchMikroTableBlock-companyPartInMatchWith-"+matchedCompanyId).removeClass("d-none");
      $("#table-companyPartInMatchWith-"+matchedCompanyId+" tr:last").after(
        `
        <tr>
            <td class="w-0 d-none">` + data.responseData.guid + `</td>
            <td class="w-25">` + data.responseData.kod + `</td>
            <td class="w-75">` + data.responseData.name + `</td>
        </tr>
        `
      );
      $("#matchMikroButton-companyPartInMatchWith-"+matchedCompanyId).attr("disabled",false);
    }else if(data.status == "not_found"){
      let matchedCompanyId = data.data.companyId;
      $("#matchMikroLoader-companyPartInMatchWith-"+matchedCompanyId).busyLoad("hide", {
        animation: "fade"
      });
      $("#matchMikroLoader-companyPartInMatchWith-"+matchedCompanyId).append(
        `
        <div class="row">
          <div class="col-md-12 text-center">
            <span>This company was not found in Mikro</span>
          </div>
        </div>
        `
      );
    }else if(data.status == "not_connected"){
      let matchedCompanyId = data.data.companyId;
      $("#matchMikroLoader-companyPartInMatchWith-"+matchedCompanyId).busyLoad("hide", {
        animation: "fade"
      });
      $("#matchMikroLoader-companyPartInMatchWith-"+matchedCompanyId).append(
        `
        <div class="row">
          <div class="col-md-12 text-center">
            <span>Failed to connect to Mikro</span>
          </div>
        </div>
        `
      );
    };
  };
};

function reload_tab(data){
  let navTagSub = $("#navTag-" + data.elementTag + "-" + data.elementTagId);
  let tabPaneSub = $("#tabPane-" + data.elementTag + "-" + data.elementTagId);

  navTagSub.remove();
  tabPaneSub.remove();

  htmx.ajax("GET", data.url + data.elementTagId + "/", {target:"#tabContSub-company", swap:"afterbegin"});
  window.history.pushState({}, '', data.url + data.elementTagId + "/");

  //spinner durdurur
  $("body").busyLoad("hide", {
    animation: "fade"
  });

  mainTopAlert.show();
};

function reload_table(data){
  if(data.location == "default"){
    $(".tableBox-inform-" + data.message.tableName + " .dataTables_scroll").busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: "rgba(69, 83, 89, 0.6)",
      color: "#455359",
      textColor: "#fff"
    });

    $('#table-' + data.message.tableName).DataTable().ajax.reload()

    $('#table-' + data.message.tableName).on( 'draw.dt', function () {
      htmx.process('#table-' + data.message.tableName);
      $(".tableBox-inform-" + data.message.tableName + " .dataTables_scroll").busyLoad("hide", {
        animation: "fade"
      });
    });
  }else if(data.location == "start"){
    $(".tableBox-inform-" + data.message.tableName + " .dataTables_scroll").busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: "rgba(69, 83, 89, 0.6)",
      color: "#455359",
      textColor: "#fff"
    });
  }else if(data.location == "stop"){
    $('#table-' + data.message.tableName).DataTable().ajax.reload()

    $('#table-' + data.message.tableName).on( 'draw.dt', function () {
      htmx.process('#table-' + data.message.tableName);
      $(".tableBox-inform-" + data.message.tableName + " .dataTables_scroll").busyLoad("hide", {
        animation: "fade"
      });
    });
  };
};

function update_mikro(data){
  if(data.location == "update_from_mikro_company"){
    if(data.status == "success"){
      mainTopAlert.update({color:"success"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-circle-check me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    }else if(data.status == "not_found"){
      mainTopAlert.update({color:"warning"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-triangle-exclamation me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    };
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl

    let navTagSub = $("#navTag-" + ee + "-" + ei);
    let tabPaneSub = $("#tabPane-" + ee + "-" + ei);

    navTagSub.remove();
    tabPaneSub.remove();

    htmx.ajax("GET", "/card/company_update/" + elementTagId + "/", {target:"#tabContSub-company", swap:"afterbegin"});
    window.history.pushState({}, '', "/card/company_update/" + elementTagId + "/");

    //spinner durdurur
    $("body").busyLoad("hide", {
      animation: "fade"
    });

    mainTopAlert.show();
  }else if(data.location == "update_to_mikro_company"){
    if(data.status == "success"){
      mainTopAlert.update({color:"success"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-circle-check me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    }else if(data.status == "not_found"){
      mainTopAlert.update({color:"warning"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-triangle-exclamation me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    };
    //spinner durdurur
    $("body").busyLoad("hide", {
      animation: "fade"
    });

    mainTopAlert.show();
  }else if(data.location == "update_from_mikro_billing"){
    if(data.status == "success"){
      mainTopAlert.update({color:"success"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-circle-check me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    }else if(data.status == "not_found"){
      mainTopAlert.update({color:"warning"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-triangle-exclamation me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    };
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl

    let navTagSub = $("#navTag-" + ee + "-" + ei);
    let tabPaneSub = $("#tabPane-" + ee + "-" + ei);

    navTagSub.remove();
    tabPaneSub.remove();

    htmx.ajax("GET", "/card/billing_update/" + elementTagId + "/", {target:"#tabContSub-billing", swap:"afterbegin"});
    window.history.pushState({}, '', "/card/billing_update/" + elementTagId + "/");

    //spinner durdurur
    $("body").busyLoad("hide", {
      animation: "fade"
    });

    mainTopAlert.show();
  }else if(data.location == "update_to_mikro_billing"){
    if(data.status == "success"){
      mainTopAlert.update({color:"success"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-circle-check me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    }else if(data.status == "not_found"){
      mainTopAlert.update({color:"warning"});
      document.getElementById('mainTopAlert').innerHTML = '<i class="fas fa-triangle-exclamation me-3"></i>' + data.message + '<button id="mainTopAlertClose" type="button" class="btn-close"></button>';
    };
    //spinner durdurur
    $("body").busyLoad("hide", {
      animation: "fade"
    });

    mainTopAlert.show();
  };
};

function reload_micho(data){
  window.location.href = "/";
};

function send_percent(data){
  if(data.location == "order_confirmation_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };

    $("#exportProgressBarOC").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountOC").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadOCExcel").on("click", function(){
        window.location.href = "/sale/order_confirmation_download_excel"
      });
      $("#downloadOCExcel").removeClass("d-none");
    };
  }else if(data.location == "quotation_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarQ").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountQ").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadQExcel").on("click", function(){
        window.location.href = "/sale/quotation_download_excel"
      });
      $("#downloadQExcel").removeClass("d-none");
    };
  }else if(data.location == "purchase_order_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarPO").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountPO").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadPOExcel").on("click", function(){
        window.location.href = "/sale/purchase_order_download_excel"
      });
      $("#downloadPOExcel").removeClass("d-none");
    };
  }else if(data.location == "financial_report_pdf"){
    console.log(data);
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    console.log("çalıştı-2");
    $("#exportProgressBarFR").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountFR").text(percentCount.toFixed(0) + "%");
    console.log("çalıştı-3");
    if(data.ready == "true"){
      $("#downloadFRPdf").on("click", function(){
        window.location.href = "/report/financial_report_download_pdf"
      });
      $("#downloadFRPdf").removeClass("d-none");
    };
  }else if(data.location == "page_load"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(singleCount == 0 && totalCount == 0){
      percentCount = 100;
    };
    $("#exportProgressBarPL").removeClass("d-none");
    $("#exportProgressBarPL").css({"width":percentCount.toFixed(0) + "%"});
    if(data.ready == "true"){
      setTimeout(function() {
        $("#exportProgressBarPL").addClass("d-none");
        $("#exportProgressBarPL").css({"width":"0"});
      }, 500);
    };
  }else if(data.location == "part_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };

    $("#exportProgressBarPart").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountPart").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadPartExcel").on("click", function(){
        window.location.href = "/data/part_download_excel"
      });
      $("#downloadPartExcel").removeClass("d-none");
    };
  }else if(data.location == "send_invoice_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarSI").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountSI").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadSIExcel").on("click", function(){
        window.location.href = "/account/send_invoice_download_excel"
      });
      $("#downloadSIExcel").removeClass("d-none");
    };
  }else if(data.location == "soa_send_invoice_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarSOASI").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountSOASI").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadSOASIExcel").on("click", function(){
        window.location.href = "/account/soa_send_invoice_download_excel"
      });
      $("#downloadSOASIExcel").removeClass("d-none");
    };
  }else if(data.location == "soa_incoming_invoice_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarSOAII").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountSOAII").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadSOAIIExcel").on("click", function(){
        window.location.href = "/account/soa_incoming_invoice_download_excel"
      });
      $("#downloadSOAIIExcel").removeClass("d-none");
    };
  }else if(data.location == "soa_send_invoice_pdf"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message.seq
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarSOASI").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountSOASI").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadSOASIExcel").on("click", function(){
        //window.location.href = "/account/soa_send_invoice_download_pdf";
        window.open(`/account/soa_send_invoice_download_pdf?v=${data.message.version}`, '_blank');
      });
      $("#downloadSOASIExcel").removeClass("d-none");
    };
  }else if(data.location == "soa_incoming_invoice_pdf"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message.seq
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };
    $("#exportProgressBarSOAII").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountSOAII").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadSOAIIExcel").on("click", function(){
        //window.location.href = "/account/soa_incoming_invoice_download_pdf";
        window.open(`/account/soa_incoming_invoice_download_pdf?v=${data.message.version}`, '_blank');
      });
      $("#downloadSOAIIExcel").removeClass("d-none");
    };
  }else if(data.location == "company_excel"){
    var percentCount = 0;
    var totalCount = data.totalCount
    var singleCount = data.message
    var percentCount = (singleCount/totalCount)*100
    if(!percentCount){
      percentCount = 100;
    };

    $("#exportProgressBarCompany").css({"width":percentCount.toFixed(0) + "%"});
    $("#percentCountCompany").text(percentCount.toFixed(0) + "%");
    if(data.ready == "true"){
      $("#downloadCompanyExcel").on("click", function(){
        window.location.href = "/card/company_download_excel"
      });
      $("#downloadCompanyExcel").removeClass("d-none");
    };
  };

};

function send_process(data){
  if(data.location == "note_add"){
    var noteId = data.message.id;
    var noteTitle = data.message.title;
    var noteText = data.message.text;
    var noteDate = data.message.date;

    $("#noteList").prepend(
      `
      <div class="accordion-item rounded-0" id="accordion-note-item-` + noteId + `">
        <h2 class="accordion-header" id="">
            <button data-mdb-collapse-init class="accordion-button collapsed rounded-0" type="button" data-mdb-toggle="collapse"
            data-mdb-target="#accordion-note-` + noteId + `" aria-expanded="false"
            aria-controls="accordion-note-` + noteId + `"
            style="height:20px;">
            ` + noteDate + ` - ` + noteTitle + `
            </button>
        </h2>
        <div id="accordion-note-` + noteId + `" class="accordion-collapse collapse" aria-labelledby="">
            <div class="accordion-body text-start" style="font-size:0.75rem;">
            <div class="row mb-3">
                <div class="col-md-12">
                  ` + noteText + `
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <button class="btn btn-sm btn-tertiary text-red-esms removeNote" type="button" data-note="` + noteId + `">
                        <i class="fa-solid fa-trash-can fs-5"></i>
                    </button>
                </div>
            </div>
            </div>
        </div>
      </div>
      `
    );

    $(".removeNote").on("click", function(){
      $(this).html('<i class="fa-solid fa-circle-notch fa-spin fs-5"></i>');
      htmx.ajax("GET", "/note/note_delete?note=" + $(this).attr("data-note"), {target : "#addUpdateDataDialog-inform"});
    });

    $("#noteAdd").text("Add");
    $("#noteAdd").attr("disabled",false);
    //$("#accordion-note-new").removeClass("show");
    $("#noteTitleAdd").val("");
    $("#noteTextAdd").val("");

  }else if(data.location == "note_delete"){
    var id = data.message.id;
    console.log($("#accordion-note-item-" + id));
    $("#accordion-note-item-" + id).remove();
  }else if(data.location == "event_add"){
    const calendarEvents = [];
    $.ajax({
      url: '/event/api/events',
      data: {'user': user},
      dataType: 'json',
      success: function(data) {
        $.each(data, function(i, event) {
          calendarEvents.push(
            {
              id: event.id,
              summary: event.title,
              description: event.description,
              start: {
                date: Calendar.dayjs(event.startDate, 'DD.MM.YYYY').format('DD/MM/YYYY'),
                dateTime: Calendar.dayjs(event.startDate, 'DD.MM.YYYY').format('DD/MM/YYYY') + " " + event.startTime,
              },
              end: {
                date: Calendar.dayjs(event.endDate, 'DD.MM.YYYY').format('DD/MM/YYYY'),
                dateTime: Calendar.dayjs(event.endDate, 'DD.MM.YYYY').format('DD/MM/YYYY') + " " + event.endTime,
              },
              color: {
                background: event.color,
                foreground: '#0b4121',
              },
            }
          );
        });
        
        const calendarElement = document.getElementById('calendar-2');
        const calendarInstance = Calendar.getInstance(calendarElement);
        calendarInstance.removeEvents();
        calendarInstance.addEvents(calendarEvents);
        
  
        if(calendarInstance._tools.lastChild.firstChild.children.length > 1){
          calendarInstance._tools.lastChild.firstChild.lastChild.remove();
        };
  
      }
    });
  }else if(data.location == "offer_note_add"){
    var offerNoteId = data.message.id;
    var offerNoteTitle = data.message.title;
    var offerNoteText = data.message.text;
    var offerNoteDate = data.message.date;
    var offerNoteUser = data.message.user;
    var offerNoteOfferId = data.message.offerId;

    $("#offerNoteList-" + offerNoteOfferId).prepend(
      `
      <div class="accordion-item rounded-0" id="accordion-offerNote-item-` + offerNoteId + `">
        <h2 class="accordion-header" id="">
            <button data-mdb-collapse-init class="accordion-button collapsed rounded-0" type="button" data-mdb-toggle="collapse"
            data-mdb-target="#accordion-offerNote-` + offerNoteId + `" aria-expanded="false"
            aria-controls="accordion-offerNote-` + offerNoteId + `"
            style="height:20px;">
            ` + offerNoteDate + ` - ` + offerNoteUser + ` - ` + offerNoteTitle + `
            </button>
        </h2>
        <div id="accordion-offerNote-` + offerNoteId + `" class="accordion-collapse collapse" aria-labelledby="">
            <div class="accordion-body text-start" style="font-size:0.75rem;">
            <div class="row mb-3">
                <div class="col-md-12">
                  ` + offerNoteText + `
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <button class="btn btn-sm btn-tertiary text-red-esms removeOfferNote" type="button" data-note="` + offerNoteId + `">
                        <i class="fa-solid fa-trash-can fs-5"></i>
                    </button>
                </div>
            </div>
            </div>
        </div>
      </div>
      `
    );

    $(".removeOfferNote").on("click", function(){
      $(this).html('<i class="fa-solid fa-circle-notch fa-spin fs-5"></i>');
      htmx.ajax("GET", "/service/active_project_note_delete?note=" + $(this).attr("data-note"), {target : "#addUpdateDataDialog-inform"});
    });

    $("#offerNoteAdd-" + offerNoteOfferId).text("Add");
    $("#offerNoteAdd-" + offerNoteOfferId).attr("disabled",false);
    //$("#accordion-note-new").removeClass("show");
    $("#offerNoteTitleAdd-" + offerNoteOfferId).val("");
    $("#offerNoteTextAdd-" + offerNoteOfferId).val("");

  }else if(data.location == "offer_note_delete"){
    var id = data.message.id;
    $("#accordion-offerNote-item-" + id).remove();
  }else if(data.location == "finishProject_note_add"){
    var finishProjectNoteId = data.message.id;
    var finishProjectNoteTitle = data.message.title;
    var finishProjectNoteText = data.message.text;
    var finishProjectNoteDate = data.message.date;
    var finishProjectNoteUser = data.message.user;
    var finishProjectNoteOfferId = data.message.finishProjectId;

    $("#finishProjectNoteList-" + finishProjectNoteOfferId).prepend(
      `
      <div class="accordion-item rounded-0" id="accordion-finishProjectNote-item-` + finishProjectNoteId + `">
        <h2 class="accordion-header" id="">
            <button data-mdb-collapse-init class="accordion-button collapsed rounded-0" type="button" data-mdb-toggle="collapse"
            data-mdb-target="#accordion-finishProjectNote-` + finishProjectNoteId + `" aria-expanded="false"
            aria-controls="accordion-finishProjectNote-` + finishProjectNoteId + `"
            style="height:20px;">
            ` + finishProjectNoteDate + ` - ` + finishProjectNoteUser + ` - ` + finishProjectNoteTitle + `
            </button>
        </h2>
        <div id="accordion-finishProjectNote-` + finishProjectNoteId + `" class="accordion-collapse collapse" aria-labelledby="">
            <div class="accordion-body text-start" style="font-size:0.75rem;">
            <div class="row mb-3">
                <div class="col-md-12">
                  ` + finishProjectNoteText + `
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <button class="btn btn-sm btn-tertiary text-red-esms removeFinishProjectNote" type="button" data-note="` + finishProjectNoteId + `">
                        <i class="fa-solid fa-trash-can fs-5"></i>
                    </button>
                </div>
            </div>
            </div>
        </div>
      </div>
      `
    );

    $(".removeFinishProjectNote").on("click", function(){
      $(this).html('<i class="fa-solid fa-circle-notch fa-spin fs-5"></i>');
      htmx.ajax("GET", "/service/finish_project_note_delete?note=" + $(this).attr("data-note"), {target : "#addUpdateDataDialog-inform"});
    });

    $("#finishProjectNoteAdd-" + finishProjectNoteOfferId).text("Add");
    $("#finishProjectNoteAdd-" + finishProjectNoteOfferId).attr("disabled",false);
    //$("#accordion-note-new").removeClass("show");
    $("#finishProjectNoteTitleAdd-" + finishProjectNoteOfferId).val("");
    $("#finishProjectNoteTextAdd-" + finishProjectNoteOfferId).val("");

  }else if(data.location == "finishProject_note_delete"){
    var id = data.message.id;
    $("#accordion-finishProjectNote-item-" + id).remove();
  }

};

function update_detail(data){
  if(data.location == "quotation_update"){
    var quotation = data.message.quotation
    var totalDiscountPrice = data.message.totalDiscountPrice
    var totalBuyingPrice = data.message.totalBuyingPrice
    var totalGrossPrice = data.message.totalGrossPrice
    var totalSellingPrice = data.message.totalSellingPrice
    var totalProfitAmountPrice = data.message.totalProfitAmountPrice
    var totalProfitPrice = data.message.totalProfitPrice
    var currency = data.message.currency
    $("#quotationTotalBuyingPrice-" + quotation).val(currency + " " + totalBuyingPrice);
    $("#quotationTotalGrossPrice-" + quotation).val(currency + " " + totalGrossPrice);
    $("#quotationTotalDiscountPrice-" + quotation).val(currency + " " + totalDiscountPrice);
    $("#quotationTotalSellingPrice-" + quotation).val(currency + " " + totalSellingPrice);
    $("#quotationTotalProfitAmountPrice-" + quotation).val(currency + " " + totalProfitAmountPrice);
    $("#quotationTotalProfitPrice-" + quotation).text("Profit (% " + totalProfitPrice + ")");
  }else if(data.location == "quotation_part_source_change"){
    var quotation = data.message.quotation;
    

    $("#table-quotationPart-" + quotation).DataTable().ajax.reload()

    $("#table-quotationPart-" + quotation).on( 'draw.dt', function () {
        htmx.process("#table-quotationPart-" + quotation);
        $(".tableBox-inform-quotationPart-" + quotation + " .dataTables_scroll").busyLoad("hide", {
          animation: "fade"
        });
    });
  }else if(data.location == "inquiry_update"){
    var inquiry = data.message.inquiry
    var totalTotalPrice = data.message.totalTotalPrice
    var currency = data.message.currency
    $("#inquiryTotalTotalPrice-" + inquiry).val(currency + " " + totalTotalPrice);
  }else if(data.location == "inquiry_duplicate"){
    var inquiry = data.message;
    //htmx.ajax("POST", "/sale/inquiry_pdf_make/" + inquiry, {target : "#addUpdateDataDialog-inform", headers : "{'X-CSRFToken': '{{ csrf_token }}'}"});
    $("#table-inquiryPart-" + inquiry).DataTable().ajax.reload()
    
    $("#table-inquiryPart-" + inquiry).on( 'draw.dt', function () {
        htmx.process("#table-inquiryPart-" + inquiry);
        $(".tableBox-inform-inquiryPart-" + inquiry + " .dataTables_scrollBody").busyLoad("hide", {
          animation: "fade"
        });
    });
  }else if(data.location == "order_confirmation_update"){
    var orderConfirmation = data.message.orderConfirmation
    var totalDiscountPrice = data.message.totalDiscountPrice
    var totalVatPrice = data.message.totalVatPrice
    var totalBuyingPrice = data.message.totalBuyingPrice
    var totalGrossPrice = data.message.totalGrossPrice
    var totalSellingPrice = data.message.totalSellingPrice
    var totalProfitAmountPrice = data.message.totalProfitAmountPrice
    var totalProfitPrice = data.message.totalProfitPrice
    var currency = data.message.currency
    $("#orderConfirmationTotalBuyingPrice-" + orderConfirmation).val(currency + " " + totalBuyingPrice);
    $("#orderConfirmationTotalGrossPrice-" + orderConfirmation).val(currency + " " + totalGrossPrice);
    $("#orderConfirmationTotalDiscountPrice-" + orderConfirmation).val(currency + " " + totalDiscountPrice);
    $("#orderConfirmationTotalVatPrice-" + orderConfirmation).val(currency + " " + totalVatPrice);
    $("#orderConfirmationTotalSellingPrice-" + orderConfirmation).val(currency + " " + totalSellingPrice);
    $("#orderConfirmationTotalProfitAmountPrice-" + orderConfirmation).val(currency + " " + totalProfitAmountPrice);
    $("#orderConfirmationTotalProfitPrice-" + orderConfirmation).text("Profit (% " + totalProfitPrice + ")");
  }else if(data.location == "purchase_order_update"){
    var purchaseOrder = data.message.purchaseOrder
    var totalDiscountPrice = data.message.totalDiscountPrice
    var totalBuyingPrice = data.message.totalBuyingPrice
    var totalTotalPrice = data.message.totalTotalPrice
    var currency = data.message.currency
    $("#purchaseOrderTotalBuyingPrice-" + purchaseOrder).val(currency + " " + totalBuyingPrice);
    $("#purchaseOrderTotalDiscountPrice-" + purchaseOrder).val(currency + " " + totalDiscountPrice);
    $("#purchaseOrderTotalTotalPrice-" + purchaseOrder).val(currency + " " + totalTotalPrice);
  }else if(data.location == "purchasing_inquiry_update"){
    var purchasingInquiry = data.message.inquiry
    var totalTotalPrice = data.message.totalTotalPrice
    var currency = data.message.currency
    $("#purchasingInquiryTotalTotalPrice-" + purchasingInquiry).val(currency + " " + totalTotalPrice);
  }else if(data.location == "purchasing_purchase_order_update"){
    var purchasingPurchaseOrder = data.message.purchaseOrder
    var totalDiscountPrice = data.message.totalDiscountPrice
    var totalBuyingPrice = data.message.totalBuyingPrice
    var totalTotalPrice = data.message.totalTotalPrice
    var currency = data.message.currency
    $("#purchasingPurchaseOrderTotalBuyingPrice-" + purchasingPurchaseOrder).val(currency + " " + totalBuyingPrice);
    $("#purchasingPurchaseOrderTotalDiscountPrice-" + purchasingPurchaseOrder).val(currency + " " + totalDiscountPrice);
    $("#purchasingPurchaseOrderTotalTotalPrice-" + purchasingPurchaseOrder).val(currency + " " + totalTotalPrice);
  }else if(data.location == "incoming_invoice_item_place"){
    var incomingInvoice = data.message.incomingInvoice;
    
    $("#table-incomingInvoicePart-" + incomingInvoice).DataTable().ajax.reload()

    $("#table-incomingInvoicePart-" + incomingInvoice).on( 'draw.dt', function () {
        htmx.process("#table-incomingInvoicePart-" + incomingInvoice);
        $(".tableBox-inform-incomingInvoicePart-" + incomingInvoice + " .dataTables_scroll").busyLoad("hide", {
          animation: "fade"
        });
    });
  }else if(data.location == "purchase_order_item_place"){
    var purchaseOrder = data.message.purchaseOrder;

    $("#table-purchasingPurchaseOrderPart-" + purchaseOrder).DataTable().ajax.reload()

    $("#table-purchasingPurchaseOrderPart-" + purchaseOrder).on( 'draw.dt', function () {
        htmx.process("#table-purchasingPurchaseOrderPart-" + purchaseOrder);
        $(".tableBox-inform-purchasingPurchaseOrderPart-" + purchaseOrder + " .dataTables_scroll").busyLoad("hide", {
          animation: "fade"
        });
    });
  }else if(data.location == "payment_update"){
    var payment = data.message.payment
    var invoiceAmount = data.message.invoiceAmount
    var creditAmount = data.message.creditAmount
    var totalAmount = data.message.totalAmount
    var currency = data.message.currency
    $("#paymentInvoiceAmount-" + payment).val(currency + " " + invoiceAmount.toLocaleString('tr-TR', { minimumFractionDigits: 2 }));
    $("#paymentCreditAmount-" + payment).val(currency + " " + creditAmount.toLocaleString('tr-TR', { minimumFractionDigits: 2 }));
    $("#paymentTotalAmount-" + payment).val(currency + " " + totalAmount.toLocaleString('tr-TR', { minimumFractionDigits: 2 }));
  }else if(data.location == "default"){
    data.message.blocks.map((block) => {
      if (block.type == "price"){
        $(`#${block.id}`).val(data.message.currency + " " + block.value.toLocaleString('tr-TR', { minimumFractionDigits: 2 }));
      }else if(block.type == "text"){
        $(`#${block.id}`).val(block.value);
      }else if(block.type == "date"){
        $(`#${block.id}`).val(block.value);
      }else if(block.type == "html"){
        $(`#${block.id}`).html(block.value);
      };
    });
  };

};

function setNoteDatatable(){
  let es = "note";
  let id = userId

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
  var qtyBlock = [
      {
        label: "title",
        name: "title",
      },
  ]
  let editor = new $.fn.dataTable.Editor({
    ajax: "/sale/api/quotation_parts/editor/",
    table: tableId,
    idSrc: "id",
    fields: qtyBlock
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

  let deleteDataButton = $('.deleteData');
  let deleteDataButtonId = ".delete-" + es;
/**/let deleteDataUrl = "/note/note_delete/";
  let serverSide = false;
/**/let apiSource = '/note/api/notes?user=' + userId + '&format=datatables';
/**/let columns = [
      {
          orderable: false,
          className: 'select-checkbox ps-1 pe-1',
          targets: 0,
          "width": "1%"
      },
      {"data" : "", className:"ps-1 pe-1",orderable: false,"visible":false},
      {"data" : "id", "visible" : false},
      {"data" : "created_date", className:"ps-1 pe-1"},
      {"data" : "title", className:"text-start ps-1 pe-1"}
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
      scrollY : "30vh",
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
      dom : 'B',
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
      // createdRow: function(row, data, index) {
      //   $('td:eq(8)', row).css('background-color', '#C8E6C9');
      //   $('td:eq(11)', row).css('background-color', '#FFCCBC');
      // },
      "ajax" : apiSource,
      "columns" : columns
    });

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
      // let i = 1;
      // table.DataTable().cells(null, 1, { search: 'applied', order: 'applied' }).every(function (cell) {
      //     this.data(i++);
      // });
      
  });

  //////////////////Tabloya Özel/////////////////
  //Tıklanan hücrede edit yapılmasını sağlar.
  table.DataTable().on( 'click', 'tbody td.editable', function (e) {
    console.log(this);
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

  //tabloyu sağa ve sola yaslamak için parent elementin paddingini kaldır
  $('.box:has(#table-note_wrapper)').css({
    'padding': '0'
  });

  // default loading spinner'ı gizler
  $("div.dataTables_processing div").hide();
  $("div.dataTables_processing").css({"box-shadow":"none"});

};

$(document).ready(function () {
  //alertWebSocket();
  mainWebSocket();

  setNoteDatatable();
});

///////////////////CALENDAR///////////////////////
const calendarEventsTest = [
    {
      summary: 'JS Conference',
      start: {
        date: Calendar.dayjs().format('DD/MM/YYYY'),
      },
      end: {
        date: Calendar.dayjs().format('DD/MM/YYYY'),
      },
      color: {
        background: '#cfe0fc',
        foreground: '#0a47a9',
      },
    },
    {
      summary: 'Vue Meetup',
      start: {
        date: Calendar.dayjs().add(1, 'day').format('DD/MM/YYYY'),
      },
      end: {
        date: Calendar.dayjs().add(5, 'day').format('DD/MM/YYYY'),
      },
      color: {
        background: '#ebcdfe',
        foreground: '#6e02b1',
      },
    },
    {
      summary: 'Angular Meetup',
      description: 'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur',
      start: {
        date: Calendar.dayjs().subtract(3, 'day').format('DD/MM/YYYY'),
        dateTime: Calendar.dayjs().subtract(3, 'day').format('DD/MM/YYYY') + ' 10:00',
      },
      end: {
        date: Calendar.dayjs().add(3, 'day').format('DD/MM/YYYY'),
        dateTime: Calendar.dayjs().add(3, 'day').format('DD/MM/YYYY') + ' 14:00',
      },
      color: {
        background: '#c7f5d9',
        foreground: '#0b4121',
      },
    },
    {
      summary: 'React Meetup',
      start: {
        date: Calendar.dayjs().add(5, 'day').format('DD/MM/YYYY'),
      },
      end: {
        date: Calendar.dayjs().add(8, 'day').format('DD/MM/YYYY'),
      },
      color: {
        background: '#fdd8de',
        foreground: '#790619',
      },
    },
    {
      summary: 'Meeting',
      start: {
        date: Calendar.dayjs().add(1, 'day').format('DD/MM/YYYY'),
        dateTime: Calendar.dayjs().add(1, 'day').format('DD/MM/YYYY') + ' 8:00',
      },
      end: {
        date: Calendar.dayjs().add(1, 'day').format('DD/MM/YYYY'),
        dateTime: Calendar.dayjs().add(1, 'day').format('DD/MM/YYYY') + ' 12:00',
      },
      color: {
        background: '#cfe0fc',
        foreground: '#0a47a9',
      },
    },
    {
      summary: 'Call',
      start: {
        date: Calendar.dayjs().add(2, 'day').format('DD/MM/YYYY'),
        dateTime: Calendar.dayjs().add(2, 'day').format('DD/MM/YYYY') + ' 11:00',
      },
      end: {
        date: Calendar.dayjs().add(2, 'day').format('DD/MM/YYYY'),
        dateTime: Calendar.dayjs().add(2, 'day').format('DD/MM/YYYY') + ' 14:00',
      },
      color: {
        background: '#292929',
        foreground: '#f5f5f5',
      },
    }
  ];

  const calendarEvents = [];
  
  $.ajax({
    url: '/event/api/events',
    data: {'user': user},
    dataType: 'json',
    success: function(data) {
      $.each(data, function(i, event) {
        //console.log(event.startTime);
        calendarEvents.push(
          {
            id: event.id,
            summary: event.title,
            description: event.description,
            start: {
              date: Calendar.dayjs(event.startDate, 'DD.MM.YYYY').format('DD/MM/YYYY'),
              dateTime: Calendar.dayjs(event.startDate, 'DD.MM.YYYY').format('DD/MM/YYYY') + " " + event.startTime,
            },
            end: {
              date: Calendar.dayjs(event.endDate, 'DD.MM.YYYY').format('DD/MM/YYYY'),
              dateTime: Calendar.dayjs(event.endDate, 'DD.MM.YYYY').format('DD/MM/YYYY') + " " + event.endTime,
            },
            color: {
              background: event.color,
              foreground: '#0b4121',
            },
          }
        );
      });
      
      const calendarElement = document.getElementById('calendar-2');
      const calendarInstance = Calendar.getInstance(calendarElement);
      calendarInstance.addEvents(calendarEvents);

      if(calendarInstance._tools.lastChild.firstChild.children.length > 1){
        calendarInstance._tools.lastChild.firstChild.lastChild.remove();
      };

    }
  });
  
  $("#calendar-2").on("addEvent.mdb.calendar", function(e){
    var eventTitle = e.event.summary;
    var eventText = e.event.description;
    var eventStartDate = e.event.start.date;
    var eventEndDate = e.event.end.date;
    var eventStartTime = new Date(e.event.start.dateTime).toLocaleTimeString("tr-TR");
    var eventEndTime = new Date(e.event.end.dateTime).toLocaleTimeString("tr-TR");
    var eventColor = e.event.color.background.substring(0, 0) + e.event.color.background.substring(1);

    htmx.ajax("GET", "/event/event_add?title=" + eventTitle +
                                      "&text=" + eventText +
                                      "&startDate=" + eventStartDate +
                                      "&endDate=" + eventEndDate +
                                      "&startTime=" + eventStartTime +
                                      "&endTime=" + eventEndTime +
                                      "&color=" + eventColor,
                                      {target : "#addUpdateDataDialog-inform"}
    
    );
  });
  
  $("#calendar-2").on("editEvent.mdb.calendar", function(e){
    var eventId = e.event.id;
    var eventTitle = e.event.summary;
    var eventText = e.event.description;
    var eventStartDate = e.event.start.date;
    var eventEndDate = e.event.end.date;
    var eventStartTime = new Date(e.event.start.dateTime).toLocaleTimeString("tr-TR");
    var eventEndTime = new Date(e.event.end.dateTime).toLocaleTimeString("tr-TR");
    var eventColor = e.event.color.background.substring(0, 0) + e.event.color.background.substring(1);

    htmx.ajax("GET", "/event/event_update?id=" + eventId +
                                        "&title=" + eventTitle +
                                        "&text=" + eventText +
                                        "&startDate=" + eventStartDate +
                                        "&endDate=" + eventEndDate +
                                        "&startTime=" + eventStartTime +
                                        "&endTime=" + eventEndTime +
                                        "&color=" + eventColor,
                                        {target : "#addUpdateDataDialog-inform"}
    
    );

  });

  $("#calendar-2").on("deleteEvent.mdb.calendar", function(e){
    var eventId = e.event.id;

    htmx.ajax("GET", "/event/event_delete?id=" + eventId, {target : "#addUpdateDataDialog-inform"}
    
    );

  });
  
///////////////////CALENDAR-END///////////////////////

///////////////////THEME///////////////////////

///////////////////THEME-END///////////////////////
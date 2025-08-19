//mesajların otomatik kaybolması
$(document).ready(function() {
    // messages timeout for 10 sec
    setTimeout(function() {
        $('.headerTop').fadeOut('slow');
    }, 2000); // <-- time in milliseconds, 1000 =  1 sec
});

//nav tab sortable yapmak
$("#tabNav").sortable();
$("#tabNav").disableSelection();

///////////////////////////////////HTMX////////////////////////////////
//tarayıcı kapanıp açıldığında sayfanın düzgün yüklenmesi için ayar
//htmx.config.refreshOnHistoryMiss = true;

//htmx dialog gösterme
const addUpdateDataModal = new bootstrap.Modal(document.getElementById("addUpdateDataModal"));
const addUpdateDataModalSmallC = new bootstrap.Modal(document.getElementById("addUpdateDataModalSmall-c"));
const addUpdateDataModalSmall = new bootstrap.Modal(document.getElementById("addUpdateDataModalSmall"));
const addUpdateDataModalXl = new bootstrap.Modal(document.getElementById("addUpdateDataModalXl"));
const addUpdateDataModalL = new bootstrap.Modal(document.getElementById("addUpdateDataModalL"));
const addUpdateDataModalFs = new bootstrap.Modal(document.getElementById("addUpdateDataModalFs"));

htmx.on("htmx:afterSwap", (e) => {
  // Response targeting #dialog => show the modal
  if (e.detail.target.id == "addUpdateDataDialog") {
    console.log(location.href);
    addUpdateDataModal.show();
  };
  if (e.detail.target.id == "addUpdateDataDialogSmall") {
    addUpdateDataModalSmall.show();
  };
  if (e.detail.target.id == "addUpdateDataDialogSmall-c") {
    addUpdateDataModalSmallC.show();
  };
  if (e.detail.target.id == "addUpdateDataDialogXl") {
    console.log(location.href);
    addUpdateDataModalXl.show();
  };
  if (e.detail.target.id == "addUpdateDataDialogL") {
    console.log(location.href);
    addUpdateDataModalL.show();
  }if (e.detail.target.id == "addUpdateDataDialogFs") {
    console.log(location.href);
    addUpdateDataModalFs.show();
  };
});

//htmx dialog gizleme
htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    if (e.detail.target.id == "addUpdateDataDialog" && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      addUpdateDataModal.hide();
      e.detail.shouldSwap = false
    };
    if (e.detail.target.id == "addUpdateDataDialogSmall" && !e.detail.xhr.response) {
      addUpdateDataModalSmall.hide();
      e.detail.shouldSwap = false;
    };
    if (e.detail.target.id == "addUpdateDataDialogSmall-c" && !e.detail.xhr.response) {
      addUpdateDataModalSmallC.hide();
      e.detail.shouldSwap = false;
    };
    if (e.detail.target.id == "addUpdateDataDialogXl" && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      addUpdateDataModalXl.hide();
      e.detail.shouldSwap = false
    };
    if (e.detail.target.id == "addUpdateDataDialogL" && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      addUpdateDataModalL.hide();
      e.detail.shouldSwap = false
    }if (e.detail.target.id == "addUpdateDataDialogFs" && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      addUpdateDataModalFs.hide();
      e.detail.shouldSwap = false
    };
});

//htmx iptalden sonra içeriği temizleme
htmx.on("hidden.bs.modal", (e) => {
    if (e.target.id == "addUpdateDataDialog") {
      console.log(location.href);
      document.getElementById("addUpdateDataDialog").innerHTML = "";
    };
    if (e.target.id == "addUpdateDataDialogSmall") {
      console.log(location.href);
      document.getElementById("addUpdateDataDialogSmall").innerHTML = "";
    };
    if (e.target.id == "addUpdateDataDialogSmall-c") {
      console.log(location.href);
      document.getElementById("addUpdateDataDialogSmall-c").innerHTML = "";
    };
    if (e.target.id == "addUpdateDataDialogXl") {
      console.log(location.href);
      document.getElementById("addUpdateDataDialogXl").innerHTML = "";
    };
    if (e.target.id == "addUpdateDataDialogL") {
      console.log(location.href);
      document.getElementById("addUpdateDataDialogL").innerHTML = "";
    }if (e.target.id == "addUpdateDataDialogFs") {
      console.log(location.href);
      document.getElementById("addUpdateDataDialogFs").innerHTML = "";
    };
});
///////////////////////////////////HTMX-END////////////////////////////////

let btnMenu = $(".btnmenu");
let btnMobileMenu = document.querySelector("#btnMobileeMenu");
let sidebarContainer = document.querySelector(".sidebarContainer");
let homeSection = document.querySelector(".home-section");
let navNav = document.querySelector(".home-section nav");
let navNav2 = document.querySelector(".navbar");
//let sidebarv2 = document.querySelector(".sidebarv2");
let sidebarv3 = document.querySelector(".sidebarv3");

let sideBarLink = $(".sidebarLink");

//siber yükseklik düzeltme
//console.log(navNav2.offsetHeight);
//sidebarv3.style = "top:" + navNav2.offsetHeight + "px;bottom:0;height:auto;"


$(document).ready(function() {
  // Menü durumunu al
  var menuState = localStorage.getItem('menuState');
  // Menü durumu yoksa varsayılan olarak kapalı olarak ayarla
  if (menuState == null) {
    menuState = 'closed';
  };
  if (menuState == "open") {
    sidebarv3.classList.add("active");
    sidebarContainer.classList.add("active");
    homeSection.classList.add("active");
    
    //$(".logo").after('<span id="logo-micho-version" class="navbar-text text-dark" style="position:absolute;padding:0;left:40%;top:4%;"><span class="text-dark" style="font-size:0.75rem;">Beta</span></span>');
    if(window.innerWidth < 768){
      sidebarv3.classList.toggle("active");
      sidebarContainer.classList.toggle("active");
      homeSection.classList.toggle("active");
    }else{
      $("#logo-navbar").after('<h5 class="m-0 mt-1 ml-1" id="logo-text-navbar" style="color:black">Global Atlantic</h5>');
    };
  };
  if (menuState == "closed") {
    sidebarv3.classList.remove("active");
    sidebarContainer.classList.remove("active");
    homeSection.classList.remove("active");
    $("#logo-text-navbar").remove();
    $("#logo-micho-version").remove();
  };
  

  //sub menu durumu

  /*****sekme durumu*****/
  // sekme durumunu getir
  var mainTabState = JSON.parse(localStorage.getItem("mainTabState"));

  // Sekme durumu yoksa varsayılan olarak boş olarak ayarla
  if (! mainTabState) {
    mainTabState = [];
    localStorage.setItem('mainTabState', JSON.stringify(mainTabState));
  };
  
  //açık olan ana sekmeleri getir
  // var mainTabs = $("#tabNav").children().map(function() {
  //   return this.id;
  // }).get();

  //sekmeyi yeniden aç
  // mainTabState.forEach(item => {
  //   let tabUrl = `${item.url}`;
  //   if($.fn.dataTable.isDataTable( '#table-' + `${item.model}` )){
  //     console.log("var mk");
  //   };
  //   htmx.ajax("GET", tabUrl, {target:"#tabCont", swap:"afterbegin", push:"true", onerror:function(){console.log("hataa")}});
  // });
  
  //burası yedek çözüm kullanma
  // async function processTabsSequentially(mainTabState) {
  //   for (let item of mainTabState) {
  //     $("#table-" + `${item.model}`).DataTable().destroy();
  //     let tabUrl = `${item.url}`;
  //     await new Promise((resolve, reject) => {
  //       htmx.ajax("GET", tabUrl, {
  //         target: "#tabCont",
  //         swap: "afterbegin",
  //         push: "true"
  //       }).then(() => {
  //         resolve();
  //       });
  //     });
  //   }
  // }
  
  // Fonksiyonu çağır
  //processTabsSequentially(mainTabState);

  /*****sekme durumu-end*****/
  
  //console.log(JSON.parse(localStorage.getItem("mainTabState")));
  

  var subMenuState = [];
  $(".li-submenu a.upMenu").each(function(index){
    subMenuState[index] = localStorage.getItem('subMenuState' + index);
    if (subMenuState[index] == null) {
      subMenuState[index] = 'closed';
    };

    if (subMenuState[index] == "open") {
      $("#downMenu", this).remove();
      $(this).append('<i class="fa-solid fa-chevron-down downMenu" id="downMenu"></i>');
      $(this).next().addClass("active");
    };
    if (subMenuState[index] == "closed") {
      $("#downMenu", this).remove();
      $(this).append('<i class="fa-solid fa-chevron-right downMenu" id="downMenu"></i>');
      $(this).next().removeClass("active");
    };


    $(this).on("click", function(){
      subMenuState[index] = localStorage.getItem('subMenuState' + index);
      if (subMenuState[index] == null) {
        subMenuState[index] = 'closed';
      };
      console.log("bastı");
      $(this).next().toggleClass("active");
      if($(this).next().hasClass("active")){
        $("#downMenu", this).remove();
        $(this).append('<i class="fa-solid fa-chevron-down downMenu" id="downMenu"></i>');
        localStorage.setItem('subMenuState' + index, 'open');
      }else{
        $("#downMenu", this).remove();
        $(this).append('<i class="fa-solid fa-chevron-right downMenu" id="downMenu"></i>');
        localStorage.setItem('subMenuState' + index, 'closed');
      };
    });
  });
});

btnMenu.click(function(){
    // Menü durumunu al
    var menuState = localStorage.getItem('menuState');
    // Menü durumu yoksa varsayılan olarak kapalı olarak ayarla
    if (menuState == null) {
      menuState = 'closed';
    };
    //sidebarv2.classList.toggle("active");
    sidebarv3.classList.toggle("active");
    sidebarContainer.classList.toggle("active");
    homeSection.classList.toggle("active");
    if(sidebarv3.classList.contains("active")){
      $("#logo-navbar").after('<h5 class="m-0 mt-1 ml-1" id="logo-text-navbar" style="color:black">Global Atlantic</h5>');
      //$(".logo").after('<span id="logo-micho-version" class="navbar-text text-dark" style="position:absolute;padding:0;left:40%;top:4%;"><span class="text-dark" style="font-size:0.75rem;">Beta</span></span>');
      localStorage.setItem('menuState', 'open');

      //sidebar arrow'ları için
      $(".downMenu").show();
      $(".sidebaricon").css({"margin-left": "5%"});
    }
    else{
      $("#logo-text-navbar").remove();
      $("#logo-micho-version").remove();
      localStorage.setItem('menuState', 'closed');
      //$(".downMenu").hide();
      $(".sidebaricon").css({"margin-left": "28%"});
    }
    //navNav.classList.toggle("active");
    
});

if(window.innerWidth <= 768){
  sideBarLink.click(function(){
    // Menü durumunu al
    var menuState = localStorage.getItem('menuState');
    // Menü durumu yoksa varsayılan olarak kapalı olarak ayarla
    if (menuState == null) {
      menuState = 'closed';
    };
    //sidebarv2.classList.toggle("active");
    sidebarv3.classList.toggle("active");
    sidebarContainer.classList.toggle("active");
    homeSection.classList.toggle("active");
    if(sidebarv3.classList.contains("active")){
      $("#logo-navbar").after('<h5 class="m-0 mt-1 ml-1" id="logo-text-navbar" style="color:black">Global Atlantic</h5>');
      //$(".logo").after('<span id="logo-micho-version" class="navbar-text text-dark" style="position:absolute;padding:0;left:40%;top:4%;"><span class="text-dark" style="font-size:0.75rem;">Beta</span></span>');
      localStorage.setItem('menuState', 'open');

      //sidebar arrow'ları için
      $(".downMenu").show();
      $(".sidebaricon").css({"margin-left": "5%"});
    }
    else{
      $("#logo-text-navbar").remove();
      $("#logo-micho-version").remove();
      localStorage.setItem('menuState', 'closed');
      //$(".downMenu").hide();
      $(".sidebaricon").css({"margin-left": "28%"});
    }
    //navNav.classList.toggle("active");
    
  });
}

// btnMobileMenu.onclick = function(){
//     //sidebarv2.classList.toggle("active");
//     sidebarv3.classList.toggle("active");
//     sidebarContainer.classList.toggle("active");
//     homeSection.classList.toggle("active");
//     //navNav.classList.toggle("active")
// };

/////////////DatataTables Editor////////////
//Datatables Editor ile yapılan değişiklerin post edilebilmesi için gerekli olan düzenleme
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
  }
});
/////////////DatataTables Editor-end////////////

function setHTMX(){
  let ee = elementTag;

  let addFormBlockID = "addFormBlock-" + ee;
  let addFormBlockSubID = "tabContSub-" + ee;
  let addFormBlockID_left = "addFormBlock-left-" + ee;
  
  let addForm = $(".addForm-" + ee);
  let addForm_left = $(".addForm-left-" + ee);
  let tableBox = $(".tableBox-" + ee);
  let tableId = "#table-" + ee;
  let table = $("#table-" + ee);
  let tableFilter = $("#table-" + ee + "_filter");

  //open
  htmx.on("htmx:afterSwap", (e) => {
    // Response targeting #dialog => show the modal
    if(e.detail.target.id == addFormBlockID){
      tableBox.eq(0).addClass("col-md-4");
      addForm.eq(0).addClass("col-md-8");
      console.log(tableId)
      $(tableId).DataTable().ajax.reload(function(){
        htmx.process(tableId);
      },false);
      tableFilter.hide();
    };
    if(e.detail.target.id == addFormBlockSubID){
      // $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("show", {
      //   animation: false,
      //   spinner: "pulsar",
      //   maxSize: "150px",
      //   minSize: "150px",
      //   text: "Loading ...",
      //   background: "rgba(69, 83, 89, 0.6)",
      //   color: "#455359",
      //   textColor: "#fff"
      // });
      // $(tableId).DataTable().ajax.reload(function(){
      //   htmx.process(tableId);
      // },false);
      $(tableId).on( 'draw.dt', function () {
        htmx.process(tableId);
        // $(".tableBox-" + ee + " .dataTables_scrollBody").busyLoad("hide", {
        //   animation: "fade"
        // });
      });
    };
    if(e.detail.target.id == addFormBlockID_left){
      tableBox.eq(0).addClass("d-none");
      addForm_left.eq(0).removeClass("d-none");
      addForm_left.eq(0).addClass("col-md-4");
      console.log("başarılı");
    };
    if("elementTagSub" in window){
      let es = elementTagSub;
      let addFormBlockInformID = "addFormBlock-inform-" + es;
      let addFormBlockInformDID = "addFormBlock-inform-d-" + es;
      let addFormBlockInformDJDID = "addFormBlock-inform-d-justDetail-" + es;
      let addFormBlockInformDJDID_bank = "addFormBlock-inform-d-justDetail-" + es + "-bank";
      let addFormBlockInformDUID = "addFormBlock-inform-d-u-" + es;
      if(e.detail.target.id == addFormBlockInformID){
        let addFormSub = $(".addForm-inform-" + es);
        let tableSubId = "#table-" + es;
        let tableSub = $("#table-" + es);
        let tableBoxSub = $(".tableBox-inform-" + es);
        let tableFilterSub = $("#table-" + es + "_filter");
        tableBoxSub.eq(0).addClass("col-md-6");
        addFormSub.eq(0).addClass("col-md-6");
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        tableFilterSub.hide();
      };
      if(e.detail.target.id == addFormBlockInformDID){
        let tableSubId = "#table-" + es;
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
      };
      if(e.detail.target.id == addFormBlockInformDJDID){
        let tableSubId = "#table-" + es;
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        
      };
      if(e.detail.target.id == addFormBlockInformDJDID_bank){
        let tableSubId = "#table-" + es;
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        
      };
      if(e.detail.target.id == addFormBlockInformDUID){
        let tableSubId = "#table-" + es;
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
      };
    };
  });

  //submitted
  htmx.on("htmx:beforeSwap", (e) => {
    // Empty response targeting #dialog => hide the modal
    if (e.detail.target.id == addFormBlockID && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      e.detail.shouldSwap = false;
      document.getElementById(addFormBlockID).innerHTML = "";
      tableBox.eq(0).removeClass("col-md-4");
      addForm.eq(0).removeClass("col-md-8");
      $(tableId).DataTable().ajax.reload(function(){
        htmx.process(tableId);
      },false);
      tableFilter.show();
      htmx.ajax("GET", "/notification/message_update_success");
    };
    if (e.detail.target.id == addFormBlockSubID && !e.detail.xhr.response) {
      let ee = elementTag
      let ei = elementTagId;
      console.log("ahahahaha-" + ei);
      console.log(e.detail.xhr.status);
      e.detail.shouldSwap = false;
      $(tableId).DataTable().ajax.reload(function(){
        htmx.process(tableId);
      },false);
      if(ei == "new"){
        console.log(e.detail.xhr);
        // let eSub = ee + "-" + ei;

        // let navTagSub = $("#navTag-" + eSub);
        // let tabPaneSub = $("#tabPane-" + eSub);

        // navTagSub.prev().children("a").addClass("active");
        // tabPaneSub.prev().addClass("show active");
        
        // navTagSub.prev().children("a").children("button").show();
        // $("#table-" + ee).DataTable().columns.adjust();
        
        // navTagSub.remove();
        // tabPaneSub.remove();


      };
    };
    if (e.detail.target.id == addFormBlockID_left && !e.detail.xhr.response) {
      console.log(e.detail.xhr.status);
      e.detail.shouldSwap = false;
      document.getElementById(addFormBlockID_left).innerHTML = "";
      tableBox.eq(0).removeClass("d-none");
      addForm_left.eq(0).removeClass("col-md-4");
      addForm_left.eq(0).addClass("d-none");
      htmx.ajax("GET", "/notification/message_update_success");
    };
    if("elementTagSub" in window){
      
      let es = elementTagSub;
      let ei = elementTagId;
      let addFormBlockInformID = "addFormBlock-inform-" + es;
      let addFormBlockInformDID = "addFormBlock-inform-d-" + es;
      let addFormBlockInformDJDID = "addFormBlock-inform-d-justDetail-" + es + "-" + ei;
      let addFormBlockInformDJDID_bank = "addFormBlock-inform-d-justDetail-" + es + "-" + ei + "-bank";
      let addFormBlockInformDUID = "addFormBlock-inform-d-u-" + es;
      if (e.detail.target.id == addFormBlockInformID && !e.detail.xhr.response) {
        let addFormSub = $(".addForm-inform-" + es);
        let tableSubId = "#table-" + es;
        let tableSub = $("#table-" + es);
        let tableBoxSub = $(".tableBox-inform-" + es);
        let tableFilterSub = $("#table-" + es + "_filter");
        console.log(e.detail.xhr.status);
        e.detail.shouldSwap = false;
        document.getElementById(addFormBlockInformID).innerHTML = "";
        tableBoxSub.eq(0).removeClass("col-md-6");
        addFormSub.eq(0).removeClass("col-md-6");
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        tableFilterSub.show();
        history.pushState({}, null, detailRefererPathSub);
      };
      if (e.detail.target.id == addFormBlockInformDID && !e.detail.xhr.response) {
        let aGet = addSubDataHxGet;
        let tableSubId = "#table-" + es;
        console.log(e.detail.xhr.status);
        e.detail.shouldSwap = false;
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        document.getElementById(addFormBlockInformDID).innerHTML = "";
        htmx.ajax('GET', aGet, "#addFormBlock-inform-d-" + es);
        history.pushState({}, null, detailRefererPathSub);
      };
      if (e.detail.target.id == addFormBlockInformDJDID && !e.detail.xhr.response) {
        let tableSubId = "#table-" + es + "-" + ei;
        
        console.log(e.detail.xhr.status);
        console.log(tableSubId);
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
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        $(tableSubId).DataTable().on( 'draw.dt', function () {
          htmx.process(tableId);
          $("body").busyLoad("hide", {
            animation: "fade"
          });
        });
        history.pushState({}, null, detailRefererPathSub);
      };
      if (e.detail.target.id == addFormBlockInformDJDID_bank && !e.detail.xhr.response) {
        let tableSubId = "#table-" + es + "-" + ei + "-bank";
        
        console.log(e.detail.xhr.status);
        console.log(tableSubId);
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
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        $(tableSubId).DataTable().on( 'draw.dt', function () {
          htmx.process(tableId);
          $("body").busyLoad("hide", {
            animation: "fade"
          });
        });
        history.pushState({}, null, detailRefererPathSub);
      };
      if (e.detail.target.id == addFormBlockInformDUID && !e.detail.xhr.response) {
        let tableSubId = "#table-" + es;
        console.log(e.detail.xhr.status);
        e.detail.shouldSwap = false;
        document.getElementById(addFormBlockInformDUID).innerHTML = "";
        htmx.ajax('GET', "/sale/request_part_add/", "#addFormBlock-inform-d-{{elementTagSub}}");
        $(tableSubId).DataTable().ajax.reload(function(){
          htmx.process(tableSubId);
        },false);
        history.pushState({}, null, detailRefererPathSub);
      };
    };
  });

  //cancelled
  htmx.on("hidden.bs.modal", (e) => {
    if (e.target.id == addFormBlockID) {
      document.getElementById(addFormBlockID).innerHTML = "";
    };
    if (e.target.id == addFormBlockID) {
      document.getElementById(addFormBlockSubID).innerHTML = "";
      $(tableId).DataTable().ajax.reload(function(){
        htmx.process(tableId);
      },false);
    };
    if (e.target.id == addFormBlockID_left) {
      document.getElementById(addFormBlockID_left).innerHTML = "";
    };
    if("elementTagSub" in window){
      let es = elementTagSub;
      let ei = elementTagId;
      let addFormBlockInformID = "addFormBlock-inform-" + es;
      let addFormBlockInformDID = "addFormBlock-inform-d-" + es;
      let addFormBlockInformDJDID = "addFormBlock-inform-d-justDetail-" + es + "-" + ei;
      let addFormBlockInformDJDID_bank = "addFormBlock-inform-d-justDetail-" + es + "-" + ei + "-bank";
      let addFormBlockInformDUID = "addFormBlock-inform-d-u-" + es;
      if (e.target.id == addFormBlockInformID) {
        document.getElementById(addFormBlockInformID).innerHTML = "";
      };
      if (e.target.id == addFormBlockInformDID) {
        document.getElementById(addFormBlockInformDID).innerHTML = "";
      };
      if (e.target.id == addFormBlockInformDJDID) {
        document.getElementById(addFormBlockInformDJDID).innerHTML = "";
      };
      if (e.target.id == addFormBlockInformDJDID_bank) {
        document.getElementById(addFormBlockInformDJDID_bank).innerHTML = "";
      };
      if (e.target.id == addFormBlockInformDUID) {
        document.getElementById(addFormBlockInformDUID).innerHTML = "";
      };
    }
    
  });
  

};

function setNavTab(){
  
  let e = elementTag;

  var ef = elementTag;
  let u = pageUrl;

  let navTag = $("#navTag-" + e);
  let navTagLink = $("#navTagLink-" + e);
  let tabPane = $("#tabPane-" + e);
  let removeNav = $("#removeNav-" + e);
  let sideBarButton = $(".nav-list li ." + e);

  $(".mainNavLink").removeClass("active");
  $(".mainTabPane").removeClass("show active");

  $("#tabNav").append(navTag);
  $("#tabCont").append(tabPane);
  navTagLink.addClass("active");
  tabPane.addClass("show active");

  $(".mainNavLink:not(.active)").children("button").hide();

  sideBarButton.attr("hx-swap", "none");
  $(".home-section").css({"overflow" : "hidden"});

  if(e = "dashboard"){
    $("#dashboardTabPane").css({"overflow" : "scroll"});
  }

  $("#table-" + e).DataTable().columns.adjust();

  removeNav.click(function(){
      navTag.prev().children("a").addClass("active");
      tabPane.prev().addClass("show active");
      
      navTag.prev().children("a").children("button").show();

      if(navTag.prev().attr("id") == "dashboardNavTag"){
        $(".home-section").css({"overflow" : "hidden"});
      };
      
      navTag.remove();
      tabPane.remove();

      sideBarButton.attr("hx-swap", "afterbegin");
      
  });

  navTagLink.on("shown.bs.tab", function(e){

    $(e.target).children("button").show();
    $(e.relatedTarget).children("button").hide();

    $("#table-" + ef).DataTable().columns.adjust();
    
    if($(e.target).attr("href").replace("#tabPane-","") != "dashboard"){
      $(".home-section").css({"overflow" : "hidden"});
    }else{
      $(".home-section").css({"overflow" : "auto"});
    };
    history.pushState({}, null, u);
  });

  navTag.css({"display" : "block"});
};

function setNavTabSub(){
  let eSub = elementTag + "-" + elementTagId;

  var efSub = elementTag;
  let uSub = pageUrl;
  console.log($("#tabNavSub-" + efSub))
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
      console.log(navTagSub.prev());
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
      console.log(tabPaneSub.prev());
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

    // document.querySelectorAll('.form-outline').forEach((formOutline) => {
    //   new mdb.Input(formOutline).update();
    // });
    
  };
};
 
  
  

function setNavTabSubDetail(){
  let eSub = elementTag + "-" + elementTagId + "-add-2";

  if(elementTag == "quotationAdd"){
    var efSub = "inquiry";
  }else if(elementTag == "inquiryAdd"){
    var efSub = "request";
  };
  
  let uSub = pageUrl;
  
  let navTagSub = $("#navTag-" + eSub);
  let navTagLinkSub = $("#navTagLink-" + eSub);
  let tabPaneSub = $("#tabPane-" + eSub);
  let removeNavSub = $("#removeNav-" + eSub);
  //let sideBarButtonSub = $(".nav-list li ." + eSub);


  $(".mainNavLinkSubDetail-" + efSub).removeClass("active");
  $(".mainTabPaneSubDetail-" + efSub).removeClass("show active");

  $("#nav-" + efSub + "-" + elementTagId + "-add").append(navTagSub);
  $("#tab-" + efSub + "-" + elementTagId + "-add").append(tabPaneSub);
  navTagLinkSub.addClass("active");
  tabPaneSub.addClass("show active");

  $(".mainNavLinkSubDetail:not(.active)").children("button").hide();

  removeNavSub.click(function(){
    navTagSub.prev().children("a").addClass("active");
    tabPaneSub.prev().addClass("show active");
    
    navTagSub.prev().children("a").children("button").show();
    
    navTagSub.remove();
    tabPaneSub.remove();

    sideBarButtonSub.attr("hx-swap", "afterbegin");
      
  });

  navTagLinkSub.on("shown.bs.tab", function(e){
      $(e.target).children("button").show();
      console.log($(e.target));

      $(e.relatedTarget).children("button").hide();

      history.pushState({}, null, uSub);
  });

  navTagSub.css({"display" : "block"});
};

// function setNavTabSubRefresh(){
//   let ee = elementTag;
//   let ei = elementTagId;

//   htmx.on("htmx:beforeSwap", (e) => {
//     if (e.detail.target.id == "tabContSub-" + ee && !e.detail.xhr.response) {
//       $("#navTag-" + elementTag + "-" + elementTagId).remove();
//       $("#tabPane-" + elementTag + "-" + elementTagId).remove();

//       htmx.ajax("GET", '/sale/quotation_update/' + elementTagId + '/', {target : "#tabContSub-" + elementTag + elementTagId, swap : "afterbegin"});
//     };
//   });

// };

function formSubmitMessage(){
  let ee = elementTag;
  let ei = elementTagId;
  let u = pageUrl
  console.log(ee + ei);

  $("#form-" + ee +  "-" + ei).submit(function (event) {
    console.log(ee + ei);
    event.preventDefault();
    if(ee == "request" && ei == "new"){

      // const loader1 = `
      //   <div class="loading-full loading-colors">
      //       <div class="spinner-border loading-icon text-dark"></div>
      //       <span class="loading-text text-dark">Loading...</span>
      //   </div>
      //   `;

      // const test2 = document.querySelector('#test-full');
      // test2.insertAdjacentHTML('beforeend', loader1);

      // const loadingFull = document.querySelector('.loading-full');

      // const loading = new mdb.Loading(loadingFull, {
      //   scroll: false,
      //   backdropID: 'full-backdrop'
      // });

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
        let eSub = "request-new";

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
        
        fetch('/sale/api/requests?ordering=-project&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            console.log(data["data"][0]["project"]["id"]);
            htmx.ajax("GET", "/sale/request_update/" + data["data"][0]["project"]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
            window.history.pushState({}, '', "/sale/request_update/" + data["data"][0]["project"]["id"] + "/");
          });

        setTimeout(function() {
          $("body").busyLoad("hide", {
            animation: "fade"
          });
        }, 1000);

      }, 2000);

    }else if(ee == "company" && ei == "new"){
      // const loader1 = `
      //   <div class="loading-full loading-colors">
      //       <div class="spinner-border loading-icon text-dark"></div>
      //       <span class="loading-text text-dark">Loading...</span>
      //   </div>
      //   `;

      // const test2 = document.querySelector('#test-full');
      // test2.insertAdjacentHTML('beforeend', loader1);

      // const loadingFull = document.querySelector('.loading-full');

      // const loading = new mdb.Loading(loadingFull, {
      //   scroll: false,
      //   backdropID: 'full-backdrop'
      // });

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
    }else if(ee == "vessel" && ei == "new"){
      // const loader1 = `
      //   <div class="loading-full loading-colors">
      //       <div class="spinner-border loading-icon text-dark"></div>
      //       <span class="loading-text text-dark">Loading...</span>
      //   </div>
      //   `;

      // const test2 = document.querySelector('#test-full');
      // test2.insertAdjacentHTML('beforeend', loader1);

      // const loadingFull = document.querySelector('.loading-full');

      // const loading = new mdb.Loading(loadingFull, {
      //   scroll: false,
      //   backdropID: 'full-backdrop'
      // });

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
        let eSub = "vessel-new";

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

        
        
        fetch('/card/api/vessels?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            console.log(data["data"][0]["id"]);
            htmx.ajax("GET", "/card/vessel_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
            window.history.pushState({}, '', "/card/vessel_update/" + data["data"][0]["id"] + "/");
            
          })
        
        setTimeout(function() {
          $("body").busyLoad("hide", {
            animation: "fade"
          });
        }, 1000);
        

      }, 2000);
    }else{
      let ee = elementTag;
      let ei = elementTagId;
      let u = pageUrl;

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
    };
    
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
          
                let eSub = ee +  "-" + ei + "-add-3";
          
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
              $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-check-circle me-1"></i>Saved!</div>');
              // Mesajı belirli bir süre sonra gizle
              console.log("eburasıu");
              setTimeout(function() {
                $("#message-container-inside-" + ee + '-' + ei + "-add-3").fadeOut("slow");
              }, 2000); // 3000 milisaniye (3 saniye) sonra mesaj kaybolacak
          }
      },
      error: function (xhr, status, error) {
          // Hata durumunda mesajı görüntüleyin
          $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-xmark-circle me-1"></i>At least one supplier and part must be selected!</div>');
      }
    });
    

    

  });
};

//seçilen hücredeki yazının seçili olmasını sağlar.
$(document).on('focus', '.DTE_Field input[type="text"]', function () {
  this.select();
});


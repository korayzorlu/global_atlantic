function select2PartItemDetail(){
    let data = "1";

    $('#id_part').select2({
        ajax: {
          url: "/warehouse/part_item_update/" + partItemId + "/",
          dataType: 'json',
          delay: 250,
          escapeMarkup: function (markup) { return markup; },
          processResults: function (data) {
            console.log(data);
            return {
            results: $.map(data, function (item) {
                // tek satırda koşul sorgulamak için; sorgu ? koşul sağlanıyorsa değer : koşul sağlanmıyorsa değer
                text = `
                    <b>Maker</b>: ${item.maker ? item.maker.name : "---"} | Type: ${item.type ? item.type.type : "--"} |
                    Part No: ${item.partNo ? item.partNo : "---"} | Description: ${item.description ? item.description : "---"} |
                    Tech. Spec.: ${item.techncialSpecification ? item.techncialSpecification : "---"}
                `
                return {id: item.id,
                        unique: item.partUnique__code + '.' + String(item.partUniqueCode).padStart(3,0),
                        maker: item.maker__name ? item.maker__name : "---",
                        type: item.type__type ? item.type__type : "---",
                        partNo: item.partNo ? item.partNo : "---",
                        description: item.description ? item.description : "---",
                        technicalSpecification: item.techncialSpecification ? item.techncialSpecification : "---"
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
                                <td style="width:0%; font-weight:bold; display:none;">ID</td>
                                <td style="width:5%; font-weight:bold;">ID</td>
                                <td style="width:15%; font-weight:bold;">Maker</td>
                                <td style="width:10%; font-weight:bold;">Type</td>
                                <td style="width:15%; font-weight:bold;">Part No</td>
                                <td style="width:35%; font-weight:bold;">Description</td>
                                <td style="width:20%; font-weight:bold;">Tech. Spec.</td>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="display:none;">${data.id}</td>
                                <td>${data.unique}</td>
                                <td>${data.maker}</td>
                                <td>${data.type}</td>
                                <td>${data.partNo}</td>
                                <td>${data.description}</td>
                                <td>${data.technicalSpecification}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
            return markup;
            },
        templateSelection: function (data) {
            console.log("data: " + data.text);
            if(data.text){
                var markup = `<strong>Part:</strong> ${data.text}`;
            }else if(data.id){
                var markup = `<strong>ID:</strong> ${data.unique} <strong>| Part:</strong> ${data.maker!="---" ? data.maker:""} ${data.type!="---" ? data.type:""} ${data.partNo!="---" ? data.partNo:""} ${data.description!="---" ? data.description:""} ${data.technicalSpecification!="---" ? data.technicalSpecification:""}`;
            }else{
            var markup = "Search for a part";
            };
            
            return markup;
        },
        minimumInputLength: 3,
        placeholder: "Search for a part",
        allowClear: true,
        closeOnSelect: false,
        minimumResultsForSearch: Infinity,
        scrollAfterSelect: true,
        width: "100%",
        dropdownCssClass: "partItemSelect2"
    });

    $(".partItemSelect2 .select2-results__option.select2-results__option--selectable").css({"font-size":"6px"});
    
};

function formSubmitMessagePartItem(){
    let ee = elementTag;
    let ei = elementTagId;
    let u = pageUrl
    
  
    $("#form-" + ee +  "-" + ei).submit(function (event) {
      console.log(ee + ei);
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
  
    $("#form-" + ee +  "-" + ei + "-add-3").submit(function (event) {
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
            $("#message-container-" + ee + '-' + ei + "-add-3").html('<div id="message-container-inside-' + ee + '-' + ei + "-add-3" + '"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
        }
      });
      
  
      
  
    });
};

function setNavTabSubPartItem(){
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

// var options = []
    
// fetch('/data/api/parts?maker=' + maker + '&type=' + type + '&format=datatables', {method : "GET"})
//   .then((response) => {
//   return response.json();
//   })
//   .then((data) => {
//     console.log(data["data"][0]["id"]);
//     for(let i = 0; i < data["data"].length; i++){
//       options.push({label : data["data"][i]["partNo"] + " - " + data["data"][i]["description"], value : data["data"][i]["id"]})
//     };

//     setPartItemPartDetailDatatable();
    
// });

$(document).ready(function () {
    //setHTMX();
    select2PartItemDetail();
    setNavTabSubPartItem();
    formSubmitMessagePartItem();
    
});
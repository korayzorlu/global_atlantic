function select2PartAdd(){
    $('#id_partUnique').select2({
        ajax: {
          url: "/data/part_add/",
          dataType: 'json',
          delay: 250,
          processResults: function (data) {
            return {
              results: $.map(data, function (item) {
                return {id: item.id, text: item.code};
              })
            };
          }
        },
        minimumInputLength: 3,
        placeholder: "Search for a part unique code",
        allowClear: true,
        closeOnSelect: false,
        minimumResultsForSearch: Infinity,
        scrollAfterSelect: true,
        width: "100%"
    });

    $('#id_techncialSpecification').select2({
        ajax: {
          url: "/data/part_add/",
          dataType: 'json',
          delay: 250,
          processResults: function (data) {
            return {
              results: $.map(data, function (item) {
                return {id: item.id, text: item.code};
              })
            };
          }
        },
        minimumInputLength: 3,
        placeholder: "Search for a part unique code",
        allowClear: true,
        closeOnSelect: false,
        minimumResultsForSearch: Infinity,
        scrollAfterSelect: true,
        width: "100%"
    });
};

function setNavTabSubPartAdd(){
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

function formSubmitMessagePartAdd(){
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
                        let eSub = "part-new";
            
                        let navTagSub = $("#navTag-" + eSub);
                        let tabPaneSub = $("#tabPane-" + eSub);
            
                        navTagSub.prev().children("a").addClass("active");
                        tabPaneSub.prev().addClass("show active");
                        
                        navTagSub.prev().children("a").children("button").show();
                        $("#table-" + ee).DataTable().ajax.reload(function() {
                            htmx.process("#table-" + ee);
                        });
                        $("#table-" + ee).DataTable().columns.adjust();
                        
                        navTagSub.remove();
                        tabPaneSub.remove();
            
                        // const backdrop = document.querySelector('#full-backdrop');
                        // backdrop.remove();
                        // loadingFull.remove();
            
                        
                        
                        // fetch('/data/api/parts?ordering=-id&sessionKey=' + sessionKey + '&user=' + user + '&format=datatables', {method : "GET"})
                        //     .then((response) => {
                        //     return response.json();
                        //     })
                        //     .then((data) => {
                        //     console.log(data["data"][0]["id"]);
                        //     htmx.ajax("GET", "/data/part_update/" + data["data"][0]["id"] + "/", {target:"#tabContSub-"+ee, swap:"afterbegin"});
                        //     window.history.pushState({}, '', "/data/part_update/" + data["data"][0]["id"] + "/");
                            
                        // });
                        
                        setTimeout(function() {
                            
                            $("body").busyLoad("hide", {
                            animation: "fade"
                            });
                        }, 1000);
                    
            
                    }, 2000);
                };
            },
            error: function (xhr, status, error) {
                // Hata durumunda mesajı görüntüleyin
                $("#message-container-" + ee + "-" + ei).html('<div id="message-container-inside-' + ee + '-' + ei +'"><i class="fas fa-xmark-circle me-1"></i>' + error + '</div>');
            }
        });

        
      
    });
  
  
};

function formValidationPartAdd(){
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach((form) => {
        form.addEventListener('submit', (event) => {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
        }, false);
    });
}

$(document).ready(function () {
    select2PartAdd();
    setHTMX();
    setNavTabSubPartAdd();
    formSubmitMessagePartAdd();
    //formValidationPartAdd();

});
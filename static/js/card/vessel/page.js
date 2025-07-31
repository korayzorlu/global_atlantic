function setVesselPage(){
    
    let e = elementTag
    let u = pageUrl

    let navTag = $("#navTag-" + e)
    let navTagLink = $("#navTagLink-" + e);
    let tabPane = $("#tabPane-" + e)
    let removeNav = $("#removeNav-" + e)
    let sideBarButton = $(".nav-list li ." + e)


    $(".mainNavLink").removeClass("active");
    $(".mainTabPane").removeClass("show active");

    $("#tabNav").append(navTag);
    $("#tabCont").append(tabPane);
    navTagLink.addClass("active");
    tabPane.addClass("show active");

    $(".mainNavLink:not(.active)").children("button").hide();

    sideBarButton.attr("hx-swap", "none");

    removeNav.click(function(){
        navTag.prev().children("a").addClass("active");
        tabPane.prev().addClass("show active");

        navTag.prev().children("a").children("button").show();

        navTag.remove();
        tabPane.remove();

        sideBarButton.attr("hx-swap", "afterbegin");
        
    });

    navTagLink.on("shown.bs.tab", function(e){
        $(e.target).children("button").show();
        $(e.relatedTarget).children("button").hide();
        history.pushState({}, null, u);
    });

    
    navTag.css({"display" : "block"});
};

$(document).ready(function () {
    setVesselPage(); 
});
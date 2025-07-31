function setOrganizationChart(){/**/
    // /**/ olan alanlar ilgili modele göre zorunlu değişecek alanlar
    let ef = elementTag;

    //tablo oluşurken loading spinner'ını açar
    $("#tabPane-" + ef).busyLoad("show", {
      animation: false,
      spinner: "pulsar",
      maxSize: "150px",
      minSize: "150px",
      text: "Loading ...",
      background: window.getComputedStyle($(".tab-content")[0]).backgroundColor,
      color: "#455359",
      textColor: "#455359"
    });



    
    $.ajax({
        url: '/user/api/profiles',
        dataType: 'json',
        success: function(data) {
            var managerName = "";
            var managerLabel = "";
            var managerAvatar = "";
            var managingDirectorChildren = [];
            var organizationChartData = {
                name: "",
                label: "",
                avatar: "",
                children: [],

            };
            $.each(data, function(i, profile) {
                if(profile.positionType){
                    if(profile.positionType.name == "Managing Director"){
                        organizationChartData.name = profile.user.first_name + " " + profile.user.last_name;
                        organizationChartData.label = profile.positionType.name;
                        if(profile.image){
                            organizationChartData.avatar = profile.image;
                        }else{
                            if(profile.gender == "female"){
                                organizationChartData.avatar = '/static/images/icons/4139947-spring-avatars/svg/035-woman.svg';
                            }else{
                                organizationChartData.avatar = '/static/images/icons/4139947-spring-avatars/svg/018-man.svg';
                            };
                        };
                    }else if(profile.positionType.name == "Finance Director" || profile.positionType.name == "Technical Director" || profile.positionType.name == "Sales Director" || profile.positionType.name == "Marketing Director"){
                        if(profile.image){
                            avatar = profile.image;
                        }else{
                            if(profile.gender == "female"){
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/035-woman.svg';
                            }else{
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/018-man.svg';
                            };
                        };
                        var profileData = {
                            label: profile.positionType.name,
                            name: profile.user.first_name + " " + profile.user.last_name,
                            avatar: avatar,
                            children: []
                        }
                        organizationChartData.children.push(profileData);

                    //buradan sonrası finance director'un altı
                    }else if(profile.positionType.name == "Accounting Director"){
                        if(profile.image){
                            avatar = profile.image;
                        }else{
                            if(profile.gender == "female"){
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/035-woman.svg';
                            }else{
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/018-man.svg';
                            };
                        };
                        var profileData = {
                            label: profile.positionType.name,
                            name: profile.user.first_name + " " + profile.user.last_name,
                            avatar: avatar,
                            children: []
                        }
                        for (var i = 0; i < organizationChartData.children.length; i++) {
                            if(organizationChartData.children[i].label == "Finance Director"){
                                organizationChartData.children[i].children.push(profileData);
                            };
                        };
                    }else if(profile.positionType.name == "Accounting Specialist"){
                        if(profile.image){
                            avatar = profile.image;
                        }else{
                            if(profile.gender == "female"){
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/035-woman.svg';
                            }else{
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/018-man.svg';
                            };
                        };
                        var profileData = {
                            label: profile.positionType.name,
                            name: profile.user.first_name + " " + profile.user.last_name,
                            avatar: avatar,
                            children: []
                        }
                        for (var i = 0; i < organizationChartData.children.length; i++) {
                            if(organizationChartData.children[i].label == "Finance Director"){
                                for (var j = 0; j < organizationChartData.children[i].children.length; j++) {
                                    if(organizationChartData.children[i].children[j].label == "Accounting Director"){
                                        organizationChartData.children[i].children[j].children.push(profileData);
                                    };
                                };
                            };
                        };
                    
                    // buradan sonrası sales director'un altı
                    }else if(profile.positionType.name == "Sales Executive"){
                        if(profile.image){
                            avatar = profile.image;
                        }else{
                            if(profile.gender == "female"){
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/035-woman.svg';
                            }else{
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/018-man.svg';
                            };
                        };
                        var profileData = {
                            label: profile.positionType.name,
                            name: profile.user.first_name + " " + profile.user.last_name,
                            avatar: avatar,
                            children: []
                        }
                        for (var i = 0; i < organizationChartData.children.length; i++) {
                            if(organizationChartData.children[i].label == "Sales Director"){
                                organizationChartData.children[i].children.push(profileData);
                            };
                        };
                    }else if(profile.positionType.name == "Sales Specialist"){
                        if(profile.image){
                            avatar = profile.image;
                        }else{
                            if(profile.gender == "female"){
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/035-woman.svg';
                            }else{
                                avatar = '/static/images/icons/4139947-spring-avatars/svg/018-man.svg';
                            };
                        };
                        var profileData = {
                            label: profile.positionType.name,
                            name: profile.user.first_name + " " + profile.user.last_name,
                            avatar: avatar,
                            children: []
                        }
                        for (var i = 0; i < organizationChartData.children.length; i++) {
                            if(organizationChartData.children[i].label == "Sales Director"){
                                for (var j = 0; j < organizationChartData.children[i].children.length; j++) {
                                    if(organizationChartData.children[i].children[j].label == "Sales Executive"){
                                        organizationChartData.children[i].children[j].children.push(profileData);
                                    };
                                };
                            };
                        };
                    };
                };
            });

            const advancedChart = document.getElementById('advancedChartExample');
            new OrganizationChart(advancedChart, {
                data: organizationChartData,
            });

            //chart görsel düzenleme
            $(".organization-card").css({"display":"inline-block"});
            $(".organization-chart-table").css({"width":"100%", "font-size":"10px"});

        }
    });

    

    //tablo oluştuğunda loading spinner'ını kapatır
    $("#tabPane-" + ef).busyLoad("hide", {
        animation: "fade"
    });


  
    

  

    

 
    




};




$(document).ready(function () {
/**/setOrganizationChart();
    setNavTab();
    setHTMX();

});
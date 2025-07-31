function setVesselDatatableSmall(){
    let vesselDeleteDataButton = $('.deleteData');
    let vesselDeleteDataUrl = "/card/vessel_delete/";

    vesselDataTable.DataTable({
        order: [[0, 'desc']],
        "serverSide" : true,
        "processing" : true,
        "select" : true,
        "ajax" : vesselApiSource,
        "columns" : vesselColumns
    });

    //datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
    vesselDataTable.DataTable().ajax.reload(function() {
        htmx.process('#vesselsTable');
    }, false);

    //veri silme butonu
    if(vesselDeleteDataButton){
        vesselDeleteDataButton.click(function (){
        console.log(vesselDataTable.DataTable().row({selected:true}).data()["id"]);
        htmx.ajax("GET", vesselDeleteDataUrl + vesselDataTable.DataTable().row({selected:true}).data()["id"], "#addUpdateDataDialog");
        });
    };

    //toplu silme(sonra ayarlanacak)
    let idList = []
    for(let i = 0; i < $("#vesselsTable").DataTable().rows({selected:true}).data().length; i++){
        idList.push($("#vesselsTable").DataTable().rows({selected:true}).data()[i]["id"]);
    };
};

setVesselDatatableSmall();

  
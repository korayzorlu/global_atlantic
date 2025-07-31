var makerTypeDeleteDataButton = $('.deleteData');
var makerTypeDeleteDataUrl = "/data/maker_type_delete/";

makerTypeDataTable.DataTable({
    order: [[1, 'asc']],
    "serverSide" : true,
    "processing" : true,
    "select" : true,
    "ajax" : makerTypeApiSource,
    "columns" : makerTypeColumns
});

//datatable serverside'dan yükleniyorsa htmx öğelerinin çalışmasını sağlar
makerTypeDataTable.DataTable().ajax.reload(function() {
    htmx.process('#makerTypesTable');
}, false);

//veri silme butonu
if(makerTypeDeleteDataButton){
    makerTypeDeleteDataButton.click(function (){
    console.log(makerTypeDataTable.DataTable().row({selected:true}).data()["id"]);
    htmx.ajax("GET", makerTypeDeleteDataUrl + makerTypeDataTable.DataTable().row({selected:true}).data()["id"], "#addUpdateDataDialog");
    });
};

//toplu silme(sonra ayarlanacak)
var idList = []
for(let i = 0; i < $("#makerTypesTable").DataTable().rows({selected:true}).data().length; i++){
    idList.push($("#makerTypesTable").DataTable().rows({selected:true}).data()[i]["id"]);
};


  
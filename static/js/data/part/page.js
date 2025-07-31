var addDataHxGet = "/data/part_add/";
var addDataHxTarget = "#addUpdateDataDialogXl";

var order = [[2, 'asc']];

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
        className: "deleteData tableTopButtons inTableButtons"
    },
    {
        extend: "csvHtml5",
        // text: '<i class="fa-solid fa-file-csv" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to csv file"></i>',
        tag: "img",
        attr: {src:"/static/images/icons/datatable/csv-file.svg"},
        className: "tableTopButtons inTableButtons",
    },
    {
        extend: "excelHtml5",
        // text: '<i class="fa-solid fa-file-excel" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to excel file"></i>',
        tag: "img",
        attr: {src:"/static/images/icons/datatable/xls.svg"},
        className: "tableTopButtons inTableButtons",
    },
    {
        extend: "pdfHtml5",
        // text: '<i class="fa-solid fa-file-pdf" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Export to pdf file"></i>',
        tag: "img",
        attr: {src:"/static/images/icons/datatable/pdf.svg"},
        className: "tableTopButtons inTableButtons",
    },
    {
        extend: "print",
        // text: '<i class="fa-solid fa-print" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Print"></i>',
        tag: "img",
        attr: {src:"/static/images/icons/datatable/printer.svg"},
        className: "tableTopButtons inTableButtons",
    }
];

var deleteDataButton = $('.deleteData');
var deleteDataUrl = "/data/part_delete/";
var serverSide = false;
var apiSource = '/data/api/parts?format=datatables';
var columns = [
    {"data" : "id"},
    {"data" : "partUniqueCode"},
    {"data" : "partUnique","data2":"partUniqueCode", render: function (data, type, row, meta){
        return '<a href="/data/part_unique_update/' + data.id + '/" style="cursor: pointer;text-decoration:underline;">' + data.code + '</a>.' + String(row.partUniqueCode).padStart(3,0) + '';}
    },
    {"data" : "partNo", render: function (data, type, row, meta){
        return '<a href="/data/part_update/' + row.id + '/" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
    },
    {"data" : "unit"},
    {"data" : "maker", render: function (data, type, row, meta){
        return '<a href="/data/maker_update/' + data.id + '/" style="cursor: pointer;text-decoration:underline;">' + data.name + '</a>';}
    },
    {"data" : "type.type"}
];

$(document).ready(function () {
    setDefaultDataTable($('#partsTable'), apiSource, columns, buttons, order);
    $('#partsTable').DataTable().column(0).visible(false);
    $('#partsTable').DataTable().column(1).visible(false);
});
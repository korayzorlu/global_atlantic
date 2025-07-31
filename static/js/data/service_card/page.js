var addDataHxGet = "/data/service_card_add/";
var addDataHxTarget = "#addUpdateDataDialogXl";

var order = [[1, 'asc']];

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
      // text: '<i class="fa-solid fa-file-arrow-up" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Bulk add"></i>',
      tag: "img",
      attr: {src:"/static/images/icons/datatable/printer.svg"},
      className: "tableTopButtons inTableButtons",
    }
];

var deleteDataButton = $('.deleteData');
var deleteDataUrl = "/data/service_card_delete/";
var serverSide = true;
var apiSource = '/data/api/service_cards?format=datatables';
var columns = [
                {"data" : "id"},
                {"data" : "group"},
                {"data" : "code", render: function (data, type, row, meta){
                    return '<a href="/data/service_card_update/' + row.id + '/" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                },          
                {"data" : "name"},
                {"data" : "about", "width" : "40%"}
];
$(document).ready(function () {
    setDefaultDataTable($('#serviceCardsTable'), apiSource, columns, buttons, order);
    $('#serviceCardsTable').DataTable().column(0).visible(false);
});
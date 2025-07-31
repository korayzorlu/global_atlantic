var addDataHxGet = "/data/maker_add/";
var addDataHxTarget = "#addUpdateDataDialogXl";
var bulkAddExcelUrl = "/data/maker_bulk_add_excel/";
var bulkAddDataHxGet = "/data/maker_bulk_add/";
var bulkAddDataHxTarget = "#addUpdateDataDialog-r";

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
    },
    '<a class="tableTopButtons" id="bulkAddExcel" href="#" style=""><i class="fa-solid fa-file-arrow-down" data-mdb-toggle="tooltip" data-mdb-placement="right" title="Download bulk add excel file"></i></a>',
    {
      text: '<i class="fa-solid fa-file-arrow-up"></i>',
      tag: "img",
          attr: {src:"/static/images/icons/datatable/upload.svg"},
      className: "tableTopButtons inTableButtons",
      action: function ( e, dt, node, config ) {
        htmx.ajax('GET', bulkAddDataHxGet, bulkAddDataHxTarget);
      }
    }
];

var deleteDataButton = $('.deleteData');
var deleteDataUrl = "/data/maker_delete/";
var serverSide = true;
var apiSource = '/data/api/makers?format=datatables';
var columns = [
                {"data" : "id"},
                {"data" : "name", render: function (data, type, row, meta){
                    return '<a href="/data/maker_update/' + row.id + '/" style="cursor: pointer;text-decoration:underline;">' + data + '</a>';}
                },          
                {"data" : "info"}
];
$(document).ready(function () {
    setDefaultDataTable($('#makersTable'), apiSource, columns, buttons, order);
    //bulk add excel şablon url
    $('#bulkAddExcel').attr("href", bulkAddExcelUrl);
});
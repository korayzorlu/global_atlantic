export let _componentDatatable = function (projects_api_url) {
  if (!$().DataTable) {
    console.warn("Warning - datatables.min.js is not loaded.");
    return;
  }

  // Setting datatable defaults
  $.extend($.fn.dataTable.defaults, {
    autoWidth: false,
    dom: '<"datatable-header"fBl><"datatable-scroll-wrap"t><"datatable-footer"ip>',
    language: {
      search: "<span>Filter:</span> _INPUT_",
      searchPlaceholder: "Type to filter...",
      lengthMenu: "<span>Show:</span> _MENU_",
      paginate: {
        first: "First",
        last: "Last",
        next: $("html").attr("dir") == "rtl" ? "&larr;" : "&rarr;",
        previous: $("html").attr("dir") == "rtl" ? "&rarr;" : "&larr;",
      },
    },
  });
  // Apply custom style to select
  $.extend($.fn.dataTableExt.oStdClasses, {
    sLengthSelect: "custom-select",
  });
  // Basic initialization
  let table = $(".dataTable").DataTable({
    serverSide: true,
    ajax: projects_api_url,
    buttons: {
      buttons: [
        {
          extend: "copyHtml5",
          text: '<i class="icon-copy3"></i>',
          className: "btn btn-light",
        },
        {
          extend: "excelHtml5",
          text: '<i class="icon-file-excel"></i>',
          className: "btn btn-light",
        },
        {
          extend: "pdfHtml5",
          text: '<i class="icon-file-pdf"></i>',
          className: "btn btn-light",
        },
        {
          extend: "colvis",
          text: '<i class="icon-three-bars"></i>',
          className: "btn btn-primary btn-icon",
        },
      ],
    },
    select: true,
    columns: [
      { data: "id", defaultContent: "-" },
      { data: "is_claim_continue", defaultContent: "-" },
      { data: "no", defaultContent: "-" },
      { data: "request.customer.name", defaultContent: "-" },
      { data: "request.vessel.name", defaultContent: "-" },
      { data: "request.maker_type.type", defaultContent: "-" },
      { data: "created_at", defaultContent: "-" },
      { data: "updated_at", defaultContent: "-" },
    ],
    lengthMenu: [8, 16, 32, 64, 128],
    columnDefs: [
      {
        targets: [1],
        visible: false,
      },
    ],
    "createdRow": function( row, data, dataIndex){
      console.log(data)
      if( data.is_claim_continue ===  true){
          $(row).addClass('bg-danger');
      }
  }
  });
};

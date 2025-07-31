// import { _componentDatatable } from "./datatable.js";

export let _componentDatatable = function (records_api) {
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
  $(".dataTable").DataTable({
    serverSide: true,
    ajax: records_api,
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
      { data: "username" },
      { data: "path" },
      { data: "method" },
      { data: "timesince" },
    ],
    ordering: false,
    lengthMenu: [7, 10, 25, 50, 100],
    columnDefs: [
      {
        orderable: false,
        targets: [3],
        // visible: false,
        searchable: false,
      },
    ],
  });
};


async function documentReady() {
  document.addEventListener("DOMContentLoaded", function () {
    _componentDatatable(records_api);
  });
}

documentReady()
  .then(() => {
    document.getElementById("loadTable").remove();
  })
  .catch((error) => {
    console.error(error);
  });

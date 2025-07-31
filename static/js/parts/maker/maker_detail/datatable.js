export const datatable = (function () {
  let datatableForContactDetail = function () {
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
    // Basic initialization
    let table = $(".dataTable").DataTable({
      buttons: {
        buttons: false,
      },

      select: true,
    });
  };

  // Select2 for length menu styling
  let _componentSelect2 = function () {
    if (!$().select2) {
      console.warn("Warning - select2.min.js is not loaded.");
      return;
    }

    // Initialize
    $(".dataTables_length select").select2({
      minimumResultsForSearch: Infinity,
      dropdownAutoWidth: true,
      width: "auto",
    });
  };

  return {
    init: function () {
      datatableForContactDetail();
      _componentSelect2();
    },
  };
})();

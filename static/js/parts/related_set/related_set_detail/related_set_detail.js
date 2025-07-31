// import { UI } from "./ui.js";
// import { datatable } from "./datatable.js";

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
    let table2 = $(".dataTableScroll").DataTable({
      scrollY: "450px",
      scrollCollapse: true,
      paging: false,
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


// const buttons = new Buttons();
//Variables
const actionButtons = document.querySelector(".actionButtons");

document.querySelector(".dataTableScroll").onload = datatable.init();

async function actionButons() {
  // actionButtons.innerHTML += `${buttons.editBTN()}`;
  // actionButtons.innerHTML += `${buttons.deleteBTN()}`;

  let companyEdit = document.querySelector(".button-edit");
  let companyDelete = document.querySelector(".button-remove");

  companyEdit.href = companyEditURL;
  companyDelete.href = companyDeleteURL;
}

actionButons().then(() => {
  // const addBTN = document.querySelector(".button-add");
  // addBTN.addEventListener("click", addMakerType);
});

$(".button-remove").click(function (e) {
  let href = this.href;
  console.log(href);
  e.preventDefault(),
    sweetCombine(
      "Are you sure?",
      "You won't be able to revert this!",
      "warning",
      "delete",
      () => (window.location = href),
      "Deleted!",
      "Set has been deleted.",
      "success",
      () => console.error("error --> Set delete canceled."),
      "Cancelled!",
      "Your set is safe :)",
      "error"
    );
});
$(".button-remove-row").click(function (e) {
  let href = this.href;
  console.log(href);
  e.preventDefault(),
    sweetCombine(
      "Are you sure?",
      "You won't be able to revert this!",
      "warning",
      "delete",
      () => (window.location = href),
      "Deleted!",
      "Company has been deleted.",
      "success",
      () => console.error("error --> Company delete canceled."),
      "Cancelled!",
      "Your company is safe :)",
      "error"
    );
});

// document.addEventListener("DOMContentLoaded", function () {
//   const del = document.querySelectorAll(".kv-file-remove");
//   del.forEach((d) => {
//     d.addEventListener("click", function (e) {
//       e.preventDefault();
//       this.closest(".file-preview-frame").remove();
//       request.delete("/sales/api/maker/14").then((data) => console.log(data));
//     });
//   });
// });

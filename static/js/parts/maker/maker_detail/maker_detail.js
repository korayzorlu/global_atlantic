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
const request = new Request(csrfToken);
//Variables
// const actionButtons = document.querySelector(".actionButtons");
// const actionButtonsForList = document.querySelector(".actionButtonsForTable");

document.querySelector(".dataTable").onload = datatable.init();

async function actionButons() {
  // actionButtons.innerHTML += `${buttons.editBTN()}`;
  // actionButtons.innerHTML += `${buttons.deleteBTN()}`;
  // actionButtonsForList.innerHTML += `<a class="button-add cursor-pointer" data-toggle="modal" data-target="#modal_default">
  //                                       <img src="{% static 'images/icons/add.svg' %}">
  //                                     </a>`;

  let companyEdit = document.querySelector(".button-edit");
  let companyDelete = document.querySelector(".button-remove");

  companyEdit.href = companyEditURL;
  companyDelete.href = companyDeleteURL;
}

actionButons().then(() => {
  $(".makerTypesDocuments").on("select2:select", function (e) {
    $(this).val()
      ? window.open($(this).val())
      : sweetToastType("You must choose a document.", "warning");
  });
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
      "Maker has been deleted.",
      "success",
      () => console.error("error --> Maker delete canceled."),
      "Cancelled!",
      "Your maker is safe :)",
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
      "Maker type has been deleted.",
      "success",
      () => console.error("error --> Maker type delete canceled."),
      "Cancelled!",
      "Your maker type is safe :)",
      "error"
    );
});

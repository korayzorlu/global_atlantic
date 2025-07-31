// import { UI } from "./ui.js";
// import { _componentDatatable } from "./datatable.js";

export let _componentDatatable = function (users_api) {
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
    ajax: users_api,
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
      { data: "id", defaultContent: "-" },
      { data: "username", defaultContent: "-" },
      { data: "full_name", defaultContent: "-" },
      { data: "first_name", defaultContent: "-" },
      { data: "last_name", defaultContent: "-" },
      { data: "email", defaultContent: "-" },
    ],
    lengthMenu: [8, 16, 32, 64, 128],
    columnDefs: [
      {
        searchable: false,
        targets: [3],
        //   visible: false,
      },
      {
        targets: [4,5],
        visible: false
      }
    ],
  });
};


// const ui = new UI();

// Event Listeners
function addEventListeners() {
  const buttonInfo = document.querySelector(".button-info");
  buttonInfo.addEventListener("click", getUserInfo);
}

async function documentReady() {
  document.addEventListener("DOMContentLoaded", function () {
    _componentDatatable(users_api);
  });
}

documentReady()
  .then(() => {
    // document.getElementById("loadTable").remove();
    // ui.addButtonsForDataTable(user_add_url);
  })
  .then(() => {
    addEventListeners();
  })
  .catch((error) => {
    console.error(error);
  });

// Required function to go to user page
function getUserInfo(e) {
  e.preventDefault();
  let currentRow = document.querySelectorAll(".selected");
  let rows = Array.from(currentRow);

  if (rows.length === 0) {
    sweetToastType("Select a user.", "warning");
  } else if (rows.length === 1) {
    window.localStorage.setItem(
      "pageStatus",
      document.getElementById("pageMainRoute").innerHTML
    );
    window.location = `/hr/user/${rows[0].children[0].innerHTML.trim()}`;
  } else {
    sweetToastType(
      "You can choose at most one user to go to the information page.",
      "warning"
    );
  }
}

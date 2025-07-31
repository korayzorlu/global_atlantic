// import { UI } from "./ui.js";
// import { _componentDatatable } from "./datatable.js";

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
        // targets: [1,2,3,4],
        // searchable: false,
      },
    ],
  });
};


// const ui = new UI();
const request = new Request(csrfToken);

// Event Listeners
function addEventListeners() {
  const buttonInfo = document.querySelector(".button-info");
  const buttonRemove = document.querySelector(".button-remove");
  buttonInfo.addEventListener("click", getProjectInfo);
  buttonRemove.addEventListener("click", removeProject);
}

async function documentReady() {
  document.addEventListener("DOMContentLoaded", function () {
    _componentDatatable(projects_api_url);
  });
}

documentReady()
  .then(() => {
    // document.getElementById("loadTable").remove();
    // ui.addButtonsForDataTable();
  })
  .then(() => {
    addEventListeners();
  })
  .catch((error) => {
    console.error(error);
  });

// Required function to go to project page
function getProjectInfo(e) {
  e.preventDefault();
  let currentRow = document.querySelectorAll(".selected");
  let rows = Array.from(currentRow);

  if (rows.length === 0) {
    sweetToastType("Select a project.", "warning");
  } else if (rows.length === 1) {
    window.localStorage.setItem(
      "pageStatus",
      document.getElementById("pageMainRoute").innerHTML
    );
    window.location = project_continue_url.replace(0, rows[0].children[0].innerHTML.trim());
  } else {
    sweetToastType(
      "You can choose at most one project to go to the information page.",
      "warning"
    );
  }
}

function removeProject(e) {
  e.preventDefault();
  let currentRow = document.querySelectorAll(".selected");
  let rows = Array.from(currentRow);

  if (rows.length === 0) {
    sweetToastType("Select a project.", "warning");
  } else if (rows.length === 1) {
    sweetCombineDynamic(
      "Are you sure?",
      "You won't be able to revert this!",
      "warning",
      "delete",
      () => {
        request
          .delete_r(project_update_api_url.replace(0, rows[0].children[0].innerHTML.trim()))
          .then((response) => {
            if (response.ok) {
              $(".dataTable").DataTable().ajax.reload();
            } else {
              response.json().then(errors => {
                fire_alert([{message:errors, icon:"error"}]);
              })
              throw new Error('Something went wrong');
            }
          })
      }
    );
  } else {
    sweetToastType(
      "You can choose at most one project to go to the information page.",
      "warning"
    );
  }
}

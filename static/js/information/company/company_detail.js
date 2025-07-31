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
// const ui = new UI();
const request = new Request(csrfToken);
//Variables
let table = document.querySelector(".table");
const actionButtons = document.querySelector(".actionButtons");
const actionButtonsForTable = document.querySelector(".actionButtonsForTable");
const actionButtonsForTableList = document.querySelector(
  ".actionButtonsForTableList"
);
const contactList = document.querySelector(".contactList");
const postContactBTN = document.getElementById("postContactBTN");

postContactBTN.addEventListener("click", addContactToTable);

async function actionButons() {
  //Company Info
  // actionButtons.innerHTML += `${buttons.editBTN()}`;
  // actionButtons.innerHTML += `${buttons.deleteBTN()}`;

  let companyEdit = document.querySelector(".button-edit");

  companyEdit.href = companyEditURL;
  // companyDelete.href = companyDeleteURL;

  //Contact List
  // actionButtonsForTable.innerHTML += `${buttons.addBTN()}`;
  // actionButtonsForTable.innerHTML += `<a class="button-list cursor-pointer" data-toggle="modal" data-target="#modal_default">
  //                                     <img src="${list_v2_svg_src}">
  //                                 </a>`;

  // Vessel List
  // actionButtonsForTableList.innerHTML += `${buttons.addBTN()}`;

  let contactAdd = actionButtonsForTable.querySelector(".button-add");
  contactAdd.href = company_add_url;
  let vesselAdd = actionButtonsForTableList.querySelector(".button-add");
  vesselAdd.href = vessel_add_url;
}

actionButons().then(() => {
  const listBTN = actionButtonsForTable.querySelector(".button-list");
  const companyDelete = document.querySelector(".button-remove");

  companyDelete.addEventListener("click", deleteCompany);
  listBTN.addEventListener("click", listContacts);
});

function listContacts() {
  request.get(contacts_api).then((data) => {
    ui.getContacts(data, contactList);
  });
}

table.onload = datatable.init();

$(document).on("click", ".button-remove-contact", function (e) {
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
      "Contact has been deleted.",
      "success",
      () => console.error("error --> Contact delete canceled."),
      "Cancelled!",
      "Your contact is safe :)",
      "error"
    );
});

$(document).on("click", ".button-remove-vessel", function (e) {
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
      "Vessel has been deleted.",
      "success",
      () => console.error("error --> Vessel delete canceled."),
      "Cancelled!",
      "Your vessel is safe :)",
      "error"
    );
});

contactList.onchange = () => {
  contactList.nextElementSibling.style.border = "none";
};

function addContactToTable(e) {
  let id = contactList.value;
  request.get(contact_api.replace(0, id)).then((data) => {
    let dataForCompany = data.company;
    dataForCompany.push(companyID);
    request
      .patch(contact_api.replace(0, id), { company: dataForCompany })
      .then((data) => {
        const tbody = document.getElementById("tbody");
        const rows = Array.from(tbody.querySelectorAll("tr"));
        const result = rows.filter((row) => row.id === id);
        const emptyRow = document.querySelector(".dataTables_empty");
        emptyRow ? emptyRow.remove() : null;
        if (!result[0]) {
          ui.addContactToTableUI(data);
          sweetToastType("Contact successfully added.", "success");
        } else {
          contactList.nextElementSibling.classList.add("animated");
          contactList.nextElementSibling.classList.add("shake");
          contactList.nextElementSibling.style.border = "1px solid #8E0E00";
          sweetToastType(
            "This contact already exists. Please choose another.",
            "warning"
          );
          setTimeout(() => {
            contactList.nextElementSibling.classList.remove("animated");
            contactList.nextElementSibling.classList.remove("shake");
          }, 1000);
        }
      })
      .catch((err) => console.log(err));
  });
}

document.getElementById("pageMainRoute").innerHTML =
  window.localStorage.getItem("pageStatus");

function deleteCompany(e) {
  e.preventDefault();
  sweetCombine(
    "Are you sure?",
    "You won't be able to revert this!",
    "warning",
    "delete",
    () =>
      request.delete(companyURL).then(() => {
        window.location = customerDataURL;
      }),
    "Deleted!",
    "Company has been deleted.",
    "success",
    () => console.error("error --> Company delete canceled."),
    "Cancelled!",
    "Your company is safe :)",
    "error"
  );
}

// import { UI } from "./ui.js";

const buttons = new Buttons();
//Variables
const actionButtons = document.querySelector(".actionButtons");

async function actionButons() {
  actionButtons.innerHTML += `${buttons.editBTN()}`;
  actionButtons.innerHTML += `${buttons.deleteBTN()}`;

  let companyEdit = document.querySelector(".button-edit");
  let companyDelete = document.querySelector(".button-remove");

  companyEdit.href = companyEditURL;
  companyDelete.href = companyDeleteURL;
}

// actionButons().then(() => {
//   const addBTN = document.querySelector(".button-add");
// });

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
      "Employee type has been deleted.",
      "success",
      () => console.error("error --> Employee type delete canceled."),
      "Cancelled!",
      "Your employee type is safe :)",
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

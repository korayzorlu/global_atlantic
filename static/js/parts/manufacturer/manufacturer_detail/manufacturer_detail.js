// import { UI } from "./ui.js";

// const buttons = new Buttons();
//Variables
const actionButtons = document.querySelector(".actionButtons");

async function actionButons() {
  // actionButtons.innerHTML += `${buttons.editBTN()}`;
  // actionButtons.innerHTML += `${buttons.deleteBTN()}`;

  let companyEdit = document.querySelector(".button-edit");
  let companyDelete = document.querySelector(".button-remove");

  companyEdit.href = companyEditURL;
  companyDelete.href = companyDeleteURL;
}

actionButons().then(() => {
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
      "Manufacturer has been deleted.",
      "success",
      () => console.error("error --> Manufacturer delete canceled."),
      "Cancelled!",
      "Your manufacturer is safe :)",
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

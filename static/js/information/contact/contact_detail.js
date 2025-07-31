
// const buttons = new Buttons();
//Variables
const actionButtons = document.querySelector(".actionButtons");

//Company Info
// actionButtons.innerHTML += `${buttons.editBTN()}`;
// actionButtons.innerHTML += `${buttons.deleteBTN()}`;

let companyEdit = document.querySelector(".button-edit");
let companyDelete = document.querySelector(".button-remove");

companyEdit.href = companyEditURL;
companyDelete.href = companyDeleteURL;

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
      "Contact has been deleted.",
      "success",
      () => console.error("error --> Contact delete canceled."),
      "Cancelled!",
      "Your contact is safe :)",
      "error"
    );
});

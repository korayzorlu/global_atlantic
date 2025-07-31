
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
      "dismantled",
      () => (window.location = href),
      "Deleted!",
      "Vessel has been dismantled.",
      "success",
      () => console.error("error --> Vessel delete canceled."),
      "Cancelled!",
      "Your vessel is safe :)",
      "error"
    );
});

if (status === "Not Available") {
  document.querySelector(".disabledVesselWrapper").innerHTML += `<div class="disabledVessel">
                                                                  <h1>Dismantled</h1>
                                                                </div>`;
}

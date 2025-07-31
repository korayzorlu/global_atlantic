const buttons = new Buttons();
export class UI {
  addButtonsForDataTable(addURL) {
    let actionButtons = document.querySelector(".actionButtons");
    actionButtons.innerHTML += `${buttons.infoBTN()}`;
    actionButtons.innerHTML += `${buttons.deleteBTN()}`;

  }
}

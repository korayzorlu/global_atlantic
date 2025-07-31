const buttons = new Buttons();
export class UI {
  addButtonsForDataTable(addURL) {
    let actionButtons = document.querySelector(".actionButtons");
    actionButtons.innerHTML += `${buttons.addBTN()}`;
    actionButtons.innerHTML += `${buttons.infoBTN()}`;

    let add = document.querySelector(".button-add");

    add.href = addURL;
  }
}

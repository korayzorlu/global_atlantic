class Buttons {
  addBTN() {
    return `<a  class="button-add">
              <img src="{% static 'images/icons/add.svg' %}">
          </a>
          `;
  }
  infoBTN() {
    return `<a  class="button-info">
              <img src="{% static 'images/icons/info.svg' %}">
          </a>
          `;
  }
  editBTN() {
    return `<a  class="button-edit">
              <img src="{% static 'images/icons/edit.svg' %}">
          </a>
          `;
  }
  editRow() {
    return `<a  class="button-edit-row">
              <img src="{% static 'images/icons/editing.svg' %}">
          </a>
          `;
  }
  deleteBTN() {
    return `<a  class="button-remove">
              <img src="{% static 'images/icons/cancel.svg' %}">
          </a>
          `;
  }
  deleteRow() {
    return `<a  class="button-remove-row">
              <img src="{% static 'images/icons/cancel.svg' %}">
          </a>
          `;
  }
  exitBTN() {
    return `<a  class="button-exit">
              <img src="{% static 'images/icons/exit.svg' %}">
          </a>
          `;
  }
  listBTN() {
    return `<a  class="button-list">
              <img src="{% static 'images/icons/list.svg' %}" >
          </a>
          `;
  }
}

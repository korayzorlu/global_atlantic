export class UI {
  constructor() {
    this.tbody = document.getElementById("tbody");
    this.tbodyList = document.getElementById("tbodyList");
  }
  getContacts(datas, element) {
    element.innerHTML = "";
    datas.forEach((data) => {
      element.innerHTML += `<option value="${data.id}">${
        data.first_name + " " + data.last_name
      }</option>`;
    });
  }
  addContactToTableUI(data) {
    this.tbody.innerHTML += `    <tr id="${data.id}">
                                      <td> 
                                      <a href="${contactDetailURL.replace(
                                        0,
                                        data.id
                                      )}"
                                        class="postForEdit">
                                        ${
                                          data.first_name + " " + data.last_name
                                        }
                                    </a>
                                    </td>
                                      <td>${data.position}</td>
                                      <td>
                                        <a href="tel:${data.phone_number}"
                                        class="postForEdit">
                                        ${data.phone_number}
                                    </a>
                                    </td>
                                      <td>
                                      <a href="mailto:${data.email}"
                                      class="postForEdit">
                                      ${data.email}
                                  </a>
                                  </td>
                                      <td class="p-0">
                                          <div class="rowActions">
                                              <a href="${contactDeleteURL.replace(
                                                0,
                                                data.id
                                              )}"
                                                  class="button-remove-row">
                                                  <img src="${removeImage}">
                                              </a>
                                          </div>
                                      </td>
                                  </tr>`;
    tbodyList.innerHTML += `
                            <tr id="${data.id}">
                              <td>${data.id}</td>
                              <td class="w-100">
                                  <div class="d-flex align-items-center">
                                      <div>
                                          <a href="${contactDetailURL.replace(
                                            0,
                                            data.id
                                          )}" class="text-default font-weight-semibold letter-icon-title">
                                          ${
                                            data.first_name +
                                            " " +
                                            data.last_name
                                          }</a>
                                          <div class="text-muted font-size-sm"><i>${
                                            data.position
                                          }</i></div>
                                      </div>
                                  </div>
                              </td>
                          </tr>`;
  }
}

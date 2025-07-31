// Variables
const request = new Request(csrfToken);

const maker_input = $("select[name='maker']");
const maker_type_input = $("select[name='maker_type']");
const customer_input = $("select[name='customer']");
const vessel_input = $("select[name='vessel']");
const person_in_contact_input = $("select[name='person_in_contact']");
const request_form_selector = "#form";

const cleanOptions = function (select_input) {
  select_input.find("option").each(function () {
    $(this).removeAttr("selected");
    $(this).removeAttr("data-select2-id");
    if ($(this).val()) {
      $(this).remove();
    }
  });
};

const fillInputs = function (data, input_names = null, status = null) {
  if (status && status != 200) {
    for (let key in input_names) {
      $(`input[name='${input_names[key]}']`).val('');
    }
  } else {
    for (let key in data) {
      if (input_names) {
        if (key in input_names) {
          $(`input[name='${input_names[key]}']`).val(data[key]);
        } else {
          continue
        }
      } else {
        $(`input[name='${key}']`).val(data[key]);
      }
    }
  }
}

const fillOptions = function (select_input, data, show_key, callback = null) {
  // get already selected value
  // to select it with new option list
  let values = getSelection(select_input);

  cleanOptions(select_input);
  dom_element = select_input.get(0)

  for (option of data) {
    selected = (values && values.includes(option.id.toString())) ? "selected" : "";
    dom_element.innerHTML += `<option value="${option.id}" ${selected}>${option[show_key]}</option>`
  }
  if (callback) {
    callback();
  }
};

const getSelection = function (select_input) {
  let values = select_input.val();
  if (values) {
    return values;
  } else {
    return null;
  }
};

init();

function init() {
  updateMakerTypes();
  updateVessels();
  updateContacts();
  setupListeners();
}


function setupListeners() {
  maker_input.change(() => {
    updateMakerTypes();
  });
  customer_input.change(() => {
    updateVessels();
    updateContacts();
  });
}

function updateMakerTypes() {
  new_value = getSelection(maker_input);
  if (!new_value) {
    cleanOptions(maker_type_input);
  } else {
    urlParams = new URLSearchParams();
    urlParams.set("maker", new_value);
    maker_types_api_url.search = urlParams;
    fetch(maker_types_api_url)
      .then((response) => response.json())
      .then((data) => fillOptions(maker_type_input, data, (show_key = "type")));
  }
}

function updateVessels() {
  new_value = getSelection(customer_input);
  if (!new_value) {
    cleanOptions(vessel_input);
  } else {
    urlParams = new URLSearchParams();
    urlParams.set("owner_company", new_value);
    vessels_api_url.search = urlParams;
    fetch(vessels_api_url)
      .then((response) => response.json())
      .then((data) => fillOptions(vessel_input, data, (show_key = "name")));
  }
}

function updateContacts() {
  new_value = getSelection(customer_input);
  if (!new_value) {
    cleanOptions(person_in_contact_input);
  } else {
    urlParams = new URLSearchParams();
    urlParams.set("company", new_value);
    contacts_api_url.search = urlParams;
    fetch(contacts_api_url)
      .then((response) => response.json())
      .then((data) => fillOptions(person_in_contact_input, data, (show_key = "full_name")));
  }
}

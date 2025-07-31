supplier_related_fields = {
  "name": {
    "name": "name",
    "type": "input"
  },
  "website": {
    "name": "website",
    "type": "input"
  }
}

maker_related_fields = {
  "name": {
    "name": "name",
    "type": "input"
  },
  "website": {
    "name": "website",
    "type": "input"
  },
  "category": {
    "name": "category",
    "type": "select"
  },
  "id": {
    "name": "maker",
    "type": "select"
  }
}

supplier_info_input = $("select[name='supplier_info']");
maker_info_input = $("select[name='maker_info']");

const cleanOptions = function (select_input) {
  select_input.find("option").each(function () {
    $(this).removeAttr("selected");
    $(this).removeAttr("data-select2-id");
    if ($(this).val()) {
      $(this).remove();
    }
  });
};

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

const selectOptions = function (select_input, data, status = null) {
  if (data && Array.isArray(data) && data[0].constructor === Object) {
    // if data is a json array, then parse the json ids
    data = data.map(obj => obj.id);
  }
  if (status && status != 200) {
    select_input.val('');
  } else {
    select_input.val(data)
  }
  select_input.select2()
};

const fillInput = function (target_input, value, status = null) {
  if (status && status != 200) {
    target_input.val('');
  } else {
    target_input.val(value);
  }
}

const getSelection = function (select_input) {
  let values = select_input.val();
  if (values) {
    return values;
  } else {
    return null;
  }
};

const switchInputAvailability = function (input, force_disable = null, force_enable = null) {
  if (force_disable) {
    input.prop('disabled', true)
  } else if (force_enable) {
    input.prop('disabled', false)
  } else {
    if (input.prop('disabled')) {
      input.prop('disabled', false)
    } else {
      input.prop('disabled', true)
    }
  }
}

init();

function init() {
  // getSupplierInfo();
  // getMakerInfo();
  setupListeners();
}

function setupListeners() {
  supplier_info_input.change(getSupplierInfo);
  maker_info_input.change(getMakerInfo);
}

function getSupplierInfo() {
  new_value = getSelection(supplier_info_input);

  // if no new value, don't continue
  if (!new_value) return

  // disable the fields before API request
  for (let [key, value] of Object.entries(supplier_related_fields)) {
    switchInputAvailability($(`${value.type}[name='${value.name}']`));
  }

  fetch(company_api_url.replace("0", new_value))
    .then((response) => response.json()
      .then((data) => {

        for (let key in data) {
          if (key in supplier_related_fields) {
            let field = supplier_related_fields[key]
            if (field.type == "select") {
              selectOptions($(`${field.type}[name='${field.name}']`), data[key], response.status)
            } else if (field.type == "input") {
              fillInput($(`${field.type}[name='${field.name}']`), data[key], response.status)
            }
          }
        }

        // enable the fields after processes
        for (let [key, value] of Object.entries(supplier_related_fields)) {
          switchInputAvailability($(`${value.type}[name='${value.name}']`));
        }
      }))
}

function getMakerInfo() {
  new_value = getSelection(maker_info_input);

  // if no new value, don't continue
  if (!new_value) return

  // disable the fields before API request
  for (let [key, value] of Object.entries(maker_related_fields)) {
    switchInputAvailability($(`${value.type}[name='${value.name}']`));
  }

  fetch(maker_api_url.replace("0", new_value))
    .then((response) => response.json()
      .then((data) => {
        for (let key in data) {
          if (key in maker_related_fields) {
            let field = maker_related_fields[key]
            if (field.type == "select") {
              selectOptions($(`${field.type}[name='${field.name}']`), data[key], response.status)
            } else if (field.type == "input") {
              fillInput($(`${field.type}[name='${field.name}']`), data[key], response.status)
            }
          }
        }

        // enable the fields after processes
        for (let [key, value] of Object.entries(maker_related_fields)) {
          switchInputAvailability($(`${value.type}[name='${value.name}']`));
        }
      }))
}
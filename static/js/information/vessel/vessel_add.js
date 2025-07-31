input_names = {
  "Vessel Name": "name",
  "Gross Tonnage": "gross_ton",
  "Summer Deadweight (t)": "deadweight",
  "Year of Built": "year_built",
  //"Yard": "shipyard",
  "Flag URL": "flag_url",
  "Flag": "flag_name"
}

imo_input = $("input[name='imo']");
manager_company_input = $("select[name='manager_company']");
owner_company_input = $("select[name='owner_company']");
person_in_contacts_input = $("select[name='person_in_contacts']");

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
  updateCompanies();
  updateContacts();
  imo_check();
  setupListeners();
}

function setupListeners() {
  manager_company_input.change(updateCompanies);
  owner_company_input.change(updateContacts);
  // https://stackoverflow.com/a/9955724/14506165
  imo_input.on('input', imo_check)
}

function updateCompanies() {
  new_value = getSelection(manager_company_input);
  if (!new_value) {
    new_value = ''
  }
  urlParams = new URLSearchParams();
  urlParams.set("company_group", new_value);
  companies_customers_api_url.search = urlParams;
  fetch(companies_customers_api_url)
    .then((response) => response.json())
    .then((data) =>
      fillOptions(
        owner_company_input,
        data,
        (show_key = "name"),
        callback = updateContacts
      )
    );
}

function updateContacts() {
  new_value = getSelection(owner_company_input);
  if (!new_value) {
    cleanOptions(person_in_contacts_input);
  } else {
    urlParams = new URLSearchParams();
    urlParams.set("company", new_value);
    contacts_api_url.search = urlParams;
    fetch(contacts_api_url)
      .then((response) => response.json())
      .then((data) => fillOptions(person_in_contacts_input, data, (show_key = "full_name")));
  }
}

function imo_check() {
  // https://stackoverflow.com/a/10834843/14506165
  if (/^\+?([0-9]\d*)$/.test(imo_input.val()) && imo_input.val().length == 7) {
    // console.log(1)
    getVesselInfo(imo_input.val());
  }
}

function getVesselInfo(imo) {
  // disable the fields
  for (let key in input_names) {
    switchInputAvailability($(`input[name='${input_names[key]}']`));
  }
  fetch(vesselfinder_imo_api.replace("0", imo))
    .then((response) => response.json()
      .then((data) => {
        for (let key in input_names) {
          switchInputAvailability($(`input[name='${input_names[key]}']`));
        }
        fillInputs(data, input_names, response.status)
      }))
}
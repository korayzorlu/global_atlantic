maker_input = $("select[name='maker']");
maker_type_input = $("select[name='maker_type']");

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
  setupListeners();
}

function setupListeners() {
  maker_input.change(updateMakerTypes);
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
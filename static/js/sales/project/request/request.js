// Variables
const request = new Request(csrfToken);

const maker_input = $("select[name='maker']");
const maker_type_input = $("select[name='maker_type']");
const customer_input = $("select[name='customer']");
const vessel_input = $("select[name='vessel']");
const person_in_contact_input = $("select[name='person_in_contact']");
const part_query_input = $("input[name='query']");
const part_quantity_input = $("input[name='quantity']");
const add_part_button = $("button[name='add_part']");
const request_form_selector = "#form";
const next_stage_button_selector = "a.next_stage";

const request_datatable_selector = '#requestDataTable';
const request_pdf_button_selector=".btn-request-pdf";
const request_excel_button_selector=".btn-request-excel";
const project_duplicate_button_selector = "#duplicateRequest";

const pdf_path=$(request_pdf_button_selector).attr("href");
const excel_path=$(request_excel_button_selector).attr("href");
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
  setupPartAutoComplete();
  setupDatatables();
  setupListeners();
}


function setupListeners() {
  $(`${request_form_selector} :input`).on("change", function (event) {
    $(request_form_selector).find(next_stage_button_selector).first().addClass("disabled");
  });
  maker_input.change(() => {
    part_query_input.val('');
    part_query_input.removeAttr('data-part-id');
    updateMakerTypes();
  });
  maker_type_input.change(() => {
    part_query_input.val('');
    part_query_input.removeAttr('data-part-id');
    setupPartAutoComplete();
  });
  customer_input.change(() => {
    updateVessels();
    updateContacts();
  });
  add_part_button.on("click", function () {
    let part_id = part_query_input.attr("data-part-id");
    let part_quantity = part_quantity_input.val();
    let table = $(request_datatable_selector).DataTable();
    createRequestPart(request_part_create_api_url, table, { "quantity": part_quantity, "request": request_id, "part": part_id });
  });

  $(project_duplicate_button_selector).on("click", function(){
    let project_id = $(project_duplicate_button_selector).attr("data-project-id");
    
    duplicateProject(project_duplicate_api_url, project_id)
  })

  $(request_datatable_selector).on("change", "[class*='dt-editable']", function () {
    if ($(this).attr("data-old") != this.value) {
      this.classList.add("border-danger");
    } else {
      this.classList.remove("border-danger");
    }
  });
  $(request_pdf_button_selector).on("click",function(){
    let table = $(request_datatable_selector).DataTable();
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(request_pdf_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate pdf file.", "warning");
    }
    else{
      var href=document.createAttribute("href");
      href.value=pdf_path;
      $(request_pdf_button_selector)[0].setAttributeNode(href);
    }
  });
  $(request_excel_button_selector).on("click",function(){
  
    let table = $(request_datatable_selector).DataTable();
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(request_excel_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate excel file.", "warning");
    }
    else{
      var href=document.createAttribute("href");
      href.value=excel_path;
      console.log(href)
      $(request_excel_button_selector)[0].setAttributeNode(href);
    }
  });
  
  $(request_datatable_selector).on("click", '.requestPartUpdate', function () {
    let row = $(this).closest("tr");
    let request_part_id = row.find('td').first().html();
    let table = $(request_datatable_selector).DataTable();
    let data = {};
    if (row.find("[class*='dt-editable']").toArray().some(function (element) {
      return $(element).val() != $(element).attr("data-old");
    })) {
      row.find("[class*='dt-editable']").each(function () {
        data[this.name] = this.value;
      });
      let button = $(this);
      updatePart(request_part_id, request_part_update_api_url, data, table, null, button).then(() => {
        row.find("[class*='dt-editable']").each(function () {
          $(this).attr("data-old", this.value);
          $(this).trigger("change");
        });
      });
    }

  });
  $(request_datatable_selector).on("click", '.requestPartDelete', function () {
    let request_part_id = $(this).closest("tr").find('td').first().html();
    let table = $(request_datatable_selector).DataTable();
    deletePart(request_part_id, request_part_update_api_url, table);
  })
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

function setupPartAutoComplete() {
  new_value = getSelection(maker_type_input);
  new_value = new_value ? new_value : 0;
  initializeAutoComplete(part_query_input, parts_api_url, { "compatibilities__maker_type": new_value }, "str", "id", "data-part-id");
}

function setupDatatables() {
  let table = $(request_datatable_selector);
  initializeRequestPartDatatables(table, request_parts_api_url, request_id);
}

function createRequestPart(_request_part_create_api_url, _table, _data, _button = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  request
    .post_r(_request_part_create_api_url, _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          _table.ajax.reload()
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    });
}

function deletePart(_part_id, _url, _table = null) {
  sweetCombineDynamic(
    "Are you sure?",
    "You won't be able to revert this!",
    "warning",
    "delete",
    () => {
      request
        .delete_r(_url.replace("0", _part_id))
        .then((response) => {
          if (response.ok) {
            if (_table) {
              _table.ajax.reload()
            }
          } else {
            response.json().then(errors => {
              fire_alert([{ message: errors, icon: "error" }]);
            })
            throw new Error('Something went wrong');
          }
        })
    }
  );
}

function updatePart(_part_id, _url, _data, _table = null, _modal = null, _button = null) {
  return new Promise((resolve, reject) => {
    let button_text = ""
    if (_button) {
      button_text = _button.html();
      _button.prop("disabled", true);
      _button.html(`<i class="icon-spinner2 spinner"></i>`);
    }
    request
      .patch_r(_url.replace(0, _part_id), _data).then((response) => {
        if (_button) {
          _button.html(button_text);
          _button.prop("disabled", false);
        }
        if (response.ok) {
          response.json().then(data => {
            if (_modal) {
              _modal.modal('hide');
            }
            resolve(data);
          })
        } else {
          response.json().then(errors => {
            fire_alert([{ message: errors, icon: "error" }]);
          })
          throw new Error('Something went wrong');
        }
      });
  })
}

function initializeAutoComplete(_element, _url, _search_params = null, _label_property = "name", _value_property = "id", _data_store_attribute = "data-id") {
  _element.autocomplete({
    autoFocus: false,
    source: function (request, response) {
      if (_search_params.constructor === ({}).constructor) {
        urlParams = new URLSearchParams();
        $.each(_search_params, function (key, value) {
          urlParams.set(key, value);
        });
        _url.search = urlParams;
      }
      $.ajax({
        url: _url,
        dataType: "json",
        data: {
          search: request.term,
        },
        success: function (data) {
          _element.removeAttr(_data_store_attribute);
          response($.map(data, function (item) {
            return {
              label: item[_label_property],
              value: item[_value_property]
            }
          }));
        },
      });
    },
    minLength: 3,
    select: function (event, ui) {
      // prevent autocomplete from updating the textbox
      event.preventDefault();

      $(this).val(ui.item.label);
      _element.attr(_data_store_attribute, ui.item.value);
    }
  });
}

function initializeRequestPartDatatables(_table, _request_parts_api_url, _request_id) {
  $.extend($.fn.dataTable.defaults, {
    autoWidth: false,
    dom: '<"datatable-header"fBl><"datatable-scroll-wrap"t><"datatable-footer"ip>',
    language: {
      search: "<span>Filter:</span> _INPUT_",
      searchPlaceholder: "Type to filter...",
      lengthMenu: "<span>Show:</span> _MENU_",
      paginate: {
        first: "First",
        last: "Last",
        next: $("html").attr("dir") == "rtl" ? "&larr;" : "&rarr;",
        previous: $("html").attr("dir") == "rtl" ? "&rarr;" : "&larr;",
      },
    },
  });
  _table.DataTable({
    searchCols: [
      null,
      {
        search: _request_id
      },
    ],
    serverSide: true,
    ajax: _request_parts_api_url,
    columns: [
      { data: "id" },
      { data: "request.project.id" },
      { data: "part.code" },
      { data: "part.name" },
      {
        data: "quantity",
        render: function (data, type, row, meta) {
          return `<input type="number" name="quantity" value="${data}" data-old="${data}" class="form-control select-search dt-editable" min="1" step="1">`;
        }
      },
      { data: "part.unit.name" }
    ],
    columnDefs: [
      {
        targets: 6,
        data: null,
        className: 'align-center',
        createdCell: function (td, cellData, rowData, row, col) {
          $(td).css('white-space', 'nowrap');
        },
        defaultContent: `
        <button class='requestPartUpdate btn p-0 mx-1'><i class='text-success icon-checkmark3'></i></button>
        <button class='requestPartDelete btn p-0 mx-1'><i class='text-danger fas fa-trash'></i></button>`
      },
      {
        targets: [1],
        visible: false
      }
    ]
  });
}
function duplicateProject( _project_duplicate_api_url, _project_id, _button = null){

  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  sweetCombineDynamic(
    "Are you sure?",
    "You won't be able to revert this!",
    "warning",
    "duplicate",
    () => {
      request 
      .post_r(_project_duplicate_api_url.replace("0", _project_id)).then((response) => { 
        if (_button) {
          _button.html(button_text);
          _button.prop("disabled", false);
        }
        if (response.ok) {
          response.json().then(data => {
             window.location = project_continue_url.replace(0, data.id); 
          })
        }
        else {
          response.json().then(errors => {
            console.log(errors)
            fire_alert([{ message: errors, icon: "error" }]);
          })
          throw new Error('Something went wrong');
        }
      });
    }
  );
}
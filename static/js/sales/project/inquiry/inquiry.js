// Variables
const request = new Request(csrfToken);

const inquiry_add_form = $("#inquiry_add_form");

const part_query_input_selector = "input[name='query']";
const part_quantity_input_selector = "input[name='quantity']";
const add_part_button_selector = "button[name='add_part']";
const save_stage_button_selector = "button.save_stage";
const next_stage_button_selector = "a.next_stage";
const previous_stage_button_selector = "a.previous_stage";
const inquiry_delete_button_selector = ".inquiryDelete";
const inquiry_datatable_selector = ".inquiryDataTable";
const tab_header_selector = "#tabHeader";
const tab_body_selector = "#tabBody";
const tab_body_form_selector = "form";
const inquiry_add_modal_selector = "#modal_inquiry_add";
const add_new_tab_button_selector = ".add-tab-button .text-success";
const inquiry_pdf_button_selector = ".button-inquiry-pdf";
const inquiry_excel_button_selector =".button-inquiry-excel";


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

const fillForm = function (_form, _data) {
  $.each(_data, function (key, value) {
    _form.find(`[name='${key}']`).first().val(value).trigger('change');
  });
}


init();

function init() {
  setupPartAutoComplete();
  setupDatatables();
  setupListeners();
}

function setupListeners() {
  $(document).ready(function(){
    openCreateForm();
  });
  inquiry_add_form.submit(function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    formData.append("project", project_id);
    let data = Object.fromEntries(formData.entries());
    let button = $(this).find("button[type='submit']").first();
    addInquiry(data, inquiry_create_api_url, button);
  });
  $('#tabBody').on("change", `${tab_body_form_selector} :input`, function (event) {
    let inquiry_tab = $(this).closest(".tab-pane");
    inquiry_tab.find(previous_stage_button_selector).first().addClass("disabled");
    inquiry_tab.find(next_stage_button_selector).first().addClass("disabled");
  });
  $('#tabBody').on("submit", tab_body_form_selector, function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    let inquiry_id = $(this).closest(".tab-pane").attr("data-inquiry-id");
    let data = Object.fromEntries(formData.entries());
    let button = $(this).find("button[type='submit']").first();
    updateInquiry(data, inquiry_update_api_url.replace(0, inquiry_id), $(this), button);
  });
  $('#tabBody').on("click", add_part_button_selector, function () {
    let tab_pane = $(this).closest(".tab-pane");
    let table = tab_pane.find(inquiry_datatable_selector).first().DataTable();
    let inquiry_id = tab_pane.attr("data-inquiry-id");
    let request_part_id = tab_pane.find(part_query_input_selector).first().attr("data-request-part-id");
    let request_part_quantity = tab_pane.find(part_quantity_input_selector).first().val();
    createInquiryPart(inquiry_part_create_api_url, table, { "inquiry": inquiry_id, "request_part": request_part_id, "quantity": request_part_quantity });
  });
  $('#tabHeader').on("click", inquiry_delete_button_selector, function () {
    let current_tab_header = $(this).closest(".nav-item");
    let current_tab_body_selector = current_tab_header.find("a").first().attr("href");
    let current_tab_body = $(tab_body_selector).find(current_tab_body_selector).first();
    let inquiry_id = current_tab_body.attr("data-inquiry-id");
    deleteInquiry(inquiry_id, inquiry_update_api_url);
  });
  $('#tabBody').on("change", "[class*='dt-editable']", function () {
    let element = this
    if (this.tagName == 'SELECT') element = $(this).closest('tr').find(`[aria-labelledby*=${this.name}]`)[0] // because of select2

    if ($(this).attr("data-old") != this.value) {
      element.classList.add("border-danger");
    } else {
      element.classList.remove("border-danger");
    }
  });
  $('#tabBody').on("click", '.partUpdate', function () {
    let row = $(this).closest("tr");
    let part_id = row.find('td').first().html();
    let table = $(this).closest('table').DataTable();
    let data = {};

    if (row.find("[class*='dt-editable']").toArray().some(function (element) {
      return $(element).val() != $(element).attr("data-old");
    })) {
      row.find("[class*='dt-editable']").each(function () {
        data[this.name] = this.value;
      });
      let button = $(this);
      updatePart(part_id, inquiry_part_update_api_url, data, table, null, button).then(() => {
        row.find("[class*='dt-editable']").each(function () {
          $(this).attr("data-old", this.value);
          $(this).trigger("change");
        });
      });
    }

  });
  $('#tabBody').on("click", '.partDelete', function () {
    let part_id = $(this).closest("tr").find('td').first().html();
    let table = $(this).closest('table').DataTable();
    deletePart(part_id, inquiry_part_update_api_url, table);
  })
   //pdf and excel buttons listeners
  $(inquiry_pdf_button_selector).on("click",function(){
    
    let table = $(inquiry_datatable_selector).DataTable();
    console.log(table)
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(inquiry_pdf_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate pdf file.", "warning");
    }
    else{
      active_tab = $('.tab-pane.active').first()
      inquiry_id = active_tab.attr("data-inquiry-id");
      
      if (inquiry_id) {
          window.open(project_inquiry_pdf_url.format(0, [project_id,inquiry_id]), '_blank').focus()
      
      }
    }
  });
  $(inquiry_excel_button_selector).on("click",function(){
  
    let table = $(inquiry_datatable_selector).DataTable();
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(inquiry_excel_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate excel file.", "warning");
    }
    else{
      active_tab = $('.tab-pane.active').first()
      inquiry_id = active_tab.attr("data-inquiry-id");
      if (inquiry_id) {
        window.open(project_inquiry_excel_url.format(0, [project_id,inquiry_id]), '_blank').focus()
    }
    }
  });
  


}

function updateInquiry(_data, _url, _form, _button = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  request
    .patch_r(_url, _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          // console.log(data);
          _form.find(previous_stage_button_selector).first().removeClass("disabled");
          _form.find(next_stage_button_selector).first().removeClass("disabled");
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    });
}

function addInquiry(_data, _url, _button = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  request
    .post_r(_url, _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          // console.log(data);
          addInquiryToPage(data);
          $(inquiry_add_modal_selector).modal('hide');
          $(inquiry_add_modal_selector).find(":input").val('');
          $(inquiry_add_modal_selector).find("span.select2").remove();
          $(inquiry_add_modal_selector).find("select").select2();
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    });
}

function addInquiryToPage(_data) {
  createInquiryTabHeader(_data.no);
  createInquiryTabBody(_data);
  $(tab_header_selector).find(`a[href='#${_data.no}']`).first().click();
}

function createInquiryTabHeader(_inquiry_id) {
  let new_tab_header = $(tab_header_selector).find(".nav-item").first().clone();
  if (!new_tab_header.length) {
    location.reload();
  }
  let tab_header_anchor = new_tab_header.find("a").first();
  tab_header_anchor.removeClass("active");
  tab_header_anchor.attr("href", `#${_inquiry_id}`);
  tab_header_anchor.html(_inquiry_id);
  new_tab_header.insertBefore($(tab_header_selector).find("li").last());
}

function createInquiryTabBody(_data) {
  let new_tab_body = $(tab_body_selector).find("div").first().clone();
  let part_query_input = new_tab_body.find(part_query_input_selector).first();
  // remove old datatable objects roughly
  new_tab_body.find(".table-responsive").first().html(new_tab_body.find(inquiry_datatable_selector).first()[0].outerHTML)
  let table = new_tab_body.find(inquiry_datatable_selector).first();
  table.removeAttr("id role aria-describedby");
  new_tab_body.find(":input").val('');
  new_tab_body.find(part_quantity_input_selector).val("1");
  fillForm(new_tab_body.find("form"), _data);
  new_tab_body.removeClass("active");
  new_tab_body.attr("id", `${_data.no}`);
  new_tab_body.attr("data-inquiry-id", `${_data.id}`);
  new_tab_body.find("tbody").first().html("");
  $(tab_body_selector).append(new_tab_body);
  $(tab_body_selector).find("span.select2").remove();
  $(tab_body_selector).find("select").select2();
  initializeAutoComplete(part_query_input, request_parts_api_url, { "request": project_id }, "str", "id", "data-request-part-id");
  initializeInquiryPartDatatables(table, inquiry_parts_api_url, _data.id)
}

function setupPartAutoComplete() {
  $.each($(part_query_input_selector), function () {
    initializeAutoComplete($(this), request_parts_api_url, { "request": project_id }, "str", "id", "data-request-part-id");
  });
}

function setupDatatables() {
  $.each($(inquiry_datatable_selector), function () {
    let inquiry_id = $(this).closest(".tab-pane").attr("data-inquiry-id");
    initializeInquiryPartDatatables($(this), inquiry_parts_api_url, inquiry_id);
  });
}

function createInquiryPart(_inquiry_part_create_api_url, _table, _data, _button = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  request
    .post_r(_inquiry_part_create_api_url, _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          _table.ajax.reload();
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

function initializeInquiryPartDatatables(_table, _inquiry_parts_api_url, _inquiry_id) {
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
    "drawCallback": function (settings) {
      this.first().find("select").select2()
    }
    , "searchCols": [
      null,
      { "search": _inquiry_id },
    ],
    "serverSide": true,
    "ajax": _inquiry_parts_api_url,
    "columns": [
      { "data": "id" },
      { "data": "inquiry.id" },
      { "data": "request_part.part.code" },
      { "data": "request_part.part.name" },
      {
        "data": "quantity",
        render: function (data, type, row, meta) {
          return `<input type="number" name="quantity" value="${data}" data-old="${data}" class="form-control dt-editable" min="1" step="1">`;
        }
      },
      {
        "data": "unit_price",
        render: function (data, type, row, meta) {
          return `<input type="number" name="unit_price" value="${data}" data-old="${data}" class="form-control dt-editable" min="1.00" step="0.01">`;
        }
      },
      { "data": "request_part.part.unit.name" },
      {
        "data": "quality",
        render: function (data, type, row, meta) {
          let select_element = `<select name="quality" class="form-control dt-editable" data-old="${data.value}">`
          for (const [key, value] of Object.entries(quality_choices)) {
            let selected = (key == data.value) ? 'selected' : ''
            select_element += `<option value="${key}" ${selected}>${value}</option>`
          }
          select_element += `</select>`
          return select_element;
        }
      },
      {
        "data": "availability_period",
        render: function (data, type, row, meta) {
          return `<input type="number" name="availability_period" value="${data}" data-old="${data}" class="form-control dt-editable" min="1" step="1">`;
        }
      },
      {
        "data": "availability",
        render: function (data, type, row, meta) {
          let select_element = `<select name="availability" class="form-control dt-editable" data-old="${data.value}">`
          for (const [key, value] of Object.entries(availability_choices)) {
            let selected = (key == data.value) ? 'selected' : ''
            select_element += `<option value="${key}" ${selected}>${value}</option>`
          }
          select_element += `</select>`
          return select_element;
        }
      }
    ],
    "columnDefs": [
      {
        "targets": [5, 7, 9],
        data: null,
        createdCell: function (td, cellData, rowData, row, col) {
          $(td).css('width', '150px');
        }
      },
      {
        "targets": 10,
        data: null,
        className: 'align-center',
        createdCell: function (td, cellData, rowData, row, col) {
          $(td).css('white-space', 'nowrap');
        },
        defaultContent: `
        <button class='partUpdate btn p-0 mx-1'><i class='text-success icon-checkmark3'></i></button>
        <button class='partDelete btn p-0 mx-1'><i class='text-danger fas fa-trash'></i></button>`
      },
      {
        targets: [1],
        className: "d-none"
      }
    ]
  })
}

function deleteInquiry(_inquiry_id, _inquiry_delete_api_url, _button = null) {
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
    "delete",
    () => {
      request
        .delete_r(_inquiry_delete_api_url.replace("0", _inquiry_id))
        .then((response) => {
          if (_button) {
            _button.html(button_text);
            _button.prop("disabled", false);
          }
          if (response.ok) {
            deleteInquiryFromPage(_inquiry_id);
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

function deleteInquiryFromPage(_inquiry_id) {
  let inquiry_tab = $(tab_body_selector).find(`div[data-inquiry-id=${_inquiry_id}]`).first();
  let inquiry_no = inquiry_tab.attr("id");
  let inquiry_header = $(tab_header_selector).find(`a[href='#${inquiry_no}']`).first().closest("li");
  inquiry_header.remove();
  inquiry_tab.remove();
  openCreateForm();
}

function openCreateForm(){
  let $items = $('.tab-pane');
  let $button = $(add_new_tab_button_selector);
  if(!$items.length)
  { 
    $button.click();
  }
}
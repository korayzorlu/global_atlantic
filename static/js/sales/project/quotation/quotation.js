// Variables
const request = new Request(csrfToken);

const quotation_add_form = $("#quotation_add_form");
const create_quotation_part_form = $("#create_quotation_part_form");
const order_confirmation_form = $("#order_confirmation_form");
const quotation_part_note_form = $("#quotation_part_note_form");
const order_not_confirmation_form =$("#order_not_confirmation_form");


const part_query_input_selector = "select[name='query']";
const part_quantity_input_selector = "input[name='quantity']";
const add_part_button_selector = "button[name='add_part']";
const save_stage_button_selector = "button.save_stage";
const next_stage_button_selector = "a.next_stage";
const previous_stage_button_selector = "a.previous_stage";
const order_confirm_button_selector = "button.order_confirm_button";
const order_cancel_button_selector = "button.order_cancel_button";
const quotation_delete_button_selector = ".quotationDelete";
const quotation_datatable_selector = ".quotationDataTable";
const inquiry_add_part_datatable_selector = ".inquiryAddPartElement";
const tab_header_selector = "#tabHeader";
const tab_body_selector = "#tabBody";
const tab_body_form_selector = "form";
const quotation_add_modal_selector = "#modal_quotation_add";
const order_confirmation_modal_selector = "#modal_order_confirmation";
const part_comparison_modal_selector = "#modal_part_comparison";
const not_confirmed_quotation_modal_selector="#modal_not_confirmed_quotation";
const reason_choices_selector = "select[name=reason_choices]"
const add_new_tab_button_selector = ".add-tab-button .text-success";
const quotation_pdf_button_selector = ".button-quotation-pdf";
const quotation_excel_button_selector =".button-quotation-excel";
const part_note_modal_selector = "#part_note_modal"
const part_note_selector = part_note_modal_selector +' textarea[name="part_note"]'
const part_note_button_selector = "#add_part_note"


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

//Global Variables except const
var quotation_part_id = 0




init();

function init() {
  setupPartAutoComplete();
  setupDatatables(); //can use for purchase
  setupListeners();
}
function setupListeners() {
  $(document).ready(function(){
    openCreateForm();
  });
  quotation_add_form.submit(function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    formData.append("project", project_id);
    let data = Object.fromEntries(formData.entries());
    let button = $(this).find("button[type='submit']").first();
    addQuotation(data, quotation_create_api_url, button);
  });
  create_quotation_part_form.submit(function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    formData.append("project", project_id);
    let data = Object.fromEntries(formData.entries());
    let inquiries = $(".inquiries");
    let parts = [];
    let active_tab = $(".tab-pane.active");
    let table = active_tab.find(quotation_datatable_selector).first().DataTable();
    
    let quotation_id = active_tab.attr("data-quotation-id");
    formData.append("quotation", quotation_id);
    inquiries.each(function (index, value) {
      console.log($(value).attr("value"));
      if ($(value).attr("value") !== 'undefined') {
        if ($(value).is(":checked") == true) parts.push({"part": $(value).attr("value"), "checked":true}); 
        else parts.push({"part": $(value).attr("value"), "checked":false}); 
      }
    });

    data.parts=parts;
    context = []
    $.each( data.parts, function( key, value ) {
      context.push({
        "quotation": quotation_id,
        "inquiry_part": value.part,
        "checked":value.checked
      });
    });
    console.log(context);
   createQuotationPart(quotation_part_bulk_create_api_url, table, context);
  });
  order_confirmation_form.submit(function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    let active_tab = $('.tab-pane.active').first();
    let quotation_id = active_tab.attr("data-quotation-id");
    formData.append("quotation", quotation_id);
    let data = Object.fromEntries(formData.entries());
    let button = $(this).find("button[type='submit']").first();
    orderConfirmation(data, order_confirmation_create_api_url, button);
  });

  order_not_confirmation_form.submit(function (event){
    event.preventDefault();
    let formData = new FormData(this);
    let active_tab = $('.tab-pane.active').first();
    let quotation_id = active_tab.attr("data-quotation-id");
    formData.append("quotation", quotation_id);
    let data = Object.fromEntries(formData.entries());
    let reason_choices = $(reason_choices_selector).val();
    data.reason_choices=reason_choices;
    let button = $(this).find("button[type='submit']").first();
    notConfirmedQuotationCreate(data, not_confirmed_quotation_create_api_url, button);
  });
 
  
  quotation_part_note_form.submit(function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    modal = $(part_note_modal_selector);
    button = $(part_note_button_selector);
    console.log(quotation_part_id);
    updatePart(quotation_part_id, quotation_part_update_api_url, data, null, modal, button);
  });

  $('#tabBody').on("click", order_cancel_button_selector, function (event) {
    let active_tab = $('.tab-pane.active').first();
    let quotation_id = active_tab.attr("data-quotation-id");
    cancelOrderConfirmation(quotation_id, order_confirmation_update_api_url);
  });
  $('#tabBody').on("change", `${tab_body_form_selector} :input`, function (event) {
    let quotation_tab = $(this).closest(".tab-pane");
    quotation_tab.find(previous_stage_button_selector).first().addClass("disabled");
    quotation_tab.find(next_stage_button_selector).first().addClass("disabled");
  });
  $('#tabBody').on("submit", tab_body_form_selector, function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    let quotation_id = $(this).closest(".tab-pane").attr("data-quotation-id");
    let data = Object.fromEntries(formData.entries());
    let button = $(this).find("button[type='submit']").first();
    updateQuotation(data, quotation_update_api_url.replace(0, quotation_id), $(this), button);
  });
  $('#tabBody').on("click", add_part_button_selector, function () {
    let tab_pane = $(this).closest(".tab-pane");
    let table = tab_pane.find(quotation_datatable_selector).first().DataTable();
    let quotation_id = tab_pane.attr("data-quotation-id");
    let inquiry_part_select = tab_pane.find(part_query_input_selector).first();
    let inquiry_part_id = inquiry_part_select.val();
    createQuotationPart(quotation_part_create_api_url, table, {
      "quotation": quotation_id,
      "inquiry_part": inquiry_part_id
    });
    inquiry_part_select.empty();
  });
  $('#tabHeader').on("click", quotation_delete_button_selector, function () {
    let current_tab_header = $(this).closest(".nav-item");
    let current_tab_body_selector = current_tab_header.find("a").first().attr("href");
    let current_tab_body = $(tab_body_selector).find(current_tab_body_selector).first();
    let quotation_id = current_tab_body.attr("data-quotation-id");
    deleteQuotation(quotation_id, quotation_update_api_url);
  });

  //data tables listeners are below:
  $('#tabBody').on("change", "[class*='dt-editable']", function () {
    if ($(this).attr("data-old") != this.value) {
      this.classList.add("border-danger");
    } else {
      this.classList.remove("border-danger");
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
      updatePart(part_id, quotation_part_update_api_url, data, table, null, button).then(() => {
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
    deletePart(part_id, quotation_part_update_api_url, table);
  })
  $('#tabBody').on("click", '.partCompare', function () {
    let request_part_id = $(this).closest("tr").find('td')[2].innerHTML;
    initializeComparisonTable(request_part_id, filtered_inquiry_parts_api_url);
  })
  $('#tabBody').on("click", '.partAddNote', function () {
    let part_id = $(this).closest("tr").find('td').first().html();
    let table = $(this).closest('table').DataTable();
    getPartNote(part_id, quotation_part_update_api_url,table)
    
  })
  $('#tabBody').on('select2:open', '.select2.auto-complete', function () { //https://github.com/select2/select2/issues/3902#issuecomment-916685126
    $('input.select2-search__field')
      .focus()
      .val($(this).attr("last-search"))
      .trigger('input')
  }).on('select2:closing', '.select2.auto-complete', function () {
    $(this).attr("last-search", $('input.select2-search__field').val())
  });

 //pdf and excel buttons listeners 

  $(quotation_pdf_button_selector).on("click",function(){
    
    let table = $(quotation_datatable_selector).DataTable();
    console.log(table)
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(quotation_pdf_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate pdf file.", "warning");
    }
    else{
      active_tab = $('.tab-pane.active').first()
      quotation_id = active_tab.attr("data-quotation-id");
      quotation_confirmed = active_tab.find(order_confirm_button_selector).first().attr("hidden")
      if (quotation_id) {
        if (quotation_confirmed) {
          window.open(project_order_confirmation_pdf_url.format(0, [project_id, quotation_id]), '_blank').focus()
        } else {
          window.open(project_quotation_pdf_url.format(0, [project_id, quotation_id]), '_blank').focus()
        }
      }
    }
  });
  $(quotation_excel_button_selector).on("click",function(){
  
    let table = $(quotation_datatable_selector).DataTable();
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(quotation_excel_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate excel file.", "warning");
    }
    else{
      active_tab = $('.tab-pane.active').first()
      quotation_id = active_tab.attr("data-quotation-id");
      quotation_confirmed = active_tab.find(order_confirm_button_selector).first().attr("hidden")
      if (quotation_id) {
        if (quotation_confirmed) {
          window.open(project_order_confirmation_excel_url.format(0, [project_id, quotation_id]), '_blank').focus()
        } else {
          window.open(project_quotation_excel_url.format(0, [project_id, quotation_id]), '_blank').focus()
        }
      }
    }
  });
 
 



$('#clean_inquiry_part').on('click', function () {
  active_tab = $('.tab-pane.active').first()
  quotation_id = active_tab.attr("data-quotation-id");
  let table = active_tab.find(quotation_datatable_selector).first().DataTable();
  deleteAllQuotationParts(quotation_id, quotation_part_bulk_delete_api_url, table);
})
}






function setupPartAutoComplete() {
  $.each($(part_query_input_selector), function () {
    initializeAutoComplete($(this), inquiry_parts_api_url, {
      "inquiry__project": project_id
    }, "str", "id", "data-inquiry-part-id");
  });
}

function setupDatatables() {
  $.each($(quotation_datatable_selector), function () {
    let quotation_id = $(this).closest(".tab-pane").attr("data-quotation-id");
    initializeQuotationPartDatatables($(this), quotation_parts_api_url, quotation_id);
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

function getPartNote(_part_id, _url, _table = null) {

      request
        .get_r(_url.replace("0", _part_id))
        .then((response) => {
          if (response.ok) {
            response.json().then(data => {
              $(part_note_selector).val(data.part_note);
              quotation_part_id = _part_id 
            })
            $(part_note_modal_selector).modal('show'); 
          } else {
            response.json().then(errors => {
              fire_alert([{ message: errors, icon: "error" }]);
            })
            throw new Error('Something went wrong');
          }
        })
    
}

function initializeAutoComplete(_element, _url, _search_params = null, _label_property = "name", _value_property = "id", _data_store_attribute = "data-id") {
  if (_search_params.constructor === ({}).constructor) {
    urlParams = new URLSearchParams();
    $.each(_search_params, function (key, value) {
      urlParams.set(key, value);
    });
    _url.search = urlParams;
  }
  _element.select2({
    placeholder: 'Select an item',
    minimumInputLength: 3,
    ajax: {
      url: _url,
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return { search: params.term };
      },
      processResults: function (response) {
        let results = [];
        for (let element of response) results.push({ id: element.id, text: element.str, title: element.inquiry.supplier.name })
        return { results: results };
      },
      cache: true
    }
  });
}
function initializeQuotationPartDatatables(_table, _quotation_parts_api_url, _quotation_id) {
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
    "searchCols": [
      null,
      {
        "search": _quotation_id
      },
    ],
    "serverSide": true,
    "ajax": _quotation_parts_api_url,
    "columns": [
      {
        "data": "id"
      },
      {
        "data": "quotation.id"
      },
      {
        "data": "inquiry_part.request_part.id"
      },
      {
        "data": "inquiry_part.inquiry",
        "render": function (data, type, row, meta) {
          return `<span data-toggle="tooltip" data-placement="top" title="${data.supplier.name}">${data.no}</span>`;
        }
      },
      {
        "data": "inquiry_part.request_part.part.code"
      },
      {
        "data": "inquiry_part.request_part.part.name"
      },
      {
        "data": "inquiry_part.quantity"
      },
      {
        "data": "unit_price"
      },
      // { "data": "total_price_1" },
      {
        "data": "profit",
        render: function (data, type, row, meta) {
          return `<input type="number" name="profit"  value="${data}" data-old="${data}" style="width:87px;" class="form-control select-search dt-editable" min="0.000" step="0.001">`;
        }
      },
      // { "data": "total_price_2" },
      {
        "data": "discount",
        render: function (data, type, row, meta) {
          return `<input type="number" name="discount" value="${data}" data-old="${data}" style="width:87px;" class="form-control select-search dt-editable" min="0.00" step="0.01">`;
        }
      },
      // { "data": "discount_value" },
      // { "data": "total_price_3" },
      {
        "data": "inquiry_part.availability_period"
      },
      {
        "data": "inquiry_part.availability",
        render: function (data, type, row, meta) {
          return data.name;
        }
      },
      {
        "data": "inquiry_part.quality",
        render: function (data, type, row, meta) {
          return data.name;
        }
      }
    ],
      "columnDefs": [
      // {
      //   searchable: false,
      //   targets: [7, 9, 11, 12],
      // },
      {
        searchable: false,
        targets: [3],
      },
      {
        "targets": [8, 9],
        data: null,
        createdCell: function (td, cellData, rowData, row, col) {
          $(td).css('width', '125px');
        }
      },
      {
        "targets": 13,
        "data": null,
        className: 'align-center',
        createdCell: function (td, cellData, rowData, row, col) {
          $(td).css('white-space', 'nowrap');
        },
        defaultContent:
          `
        <button class='partCompare btn p-0 mx-1'><i class='text-yellow icon-git-compare'></i></button>
        <button class='partAddNote btn p-0 mx-1'><i class='text-muted icon-notebook'></i></button>
        <button class='partUpdate btn p-0 mx-1'><i class='text-success icon-checkmark3'></i></button>
        <button class='partDelete btn p-0 mx-1'><i class='text-danger fas fa-trash'></i></button>`
      },
      {
        targets: [0, 1, 2],
        className: "d-none"
      }
    ]
  });
} 
  
$('.add_part_button').on("click", function (event) {
  active_tab = $('.tab-pane.active').first()
  quotation_id = active_tab.attr("data-quotation-id");
  request
    .get_r(inquiry_add_parts_api_url + quotation_id)
    .then((response) => {
      if (response.ok) {
        response.json().then(data => {
          buildAddInquiryTable(data);
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    })

});

$('.add_inquiry_part').on("click", function (event) {
  request
    .post_r(quotation_create_api_url)
    .then((response) => {
      if (response.ok) {
        response.json().then(data => {
          buildAddInquiryTable(data);
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    }) 

});






function initializeInquiryAddPartDatatables(_table, inquiry_parts_api_url) {
  _table.DataTable({
    "serverSide": true,
    "ajax": inquiry_parts_api_url,
    "columns": [
      {
        "data": "id"
      },
      {
        "data": "quotation.id"
      },
      {
        "data": "inquiry_part.request_part.id"
      },
      {
        "data": "inquiry_part.inquiry",
        "render": function (data, type, row, meta) {
          return `<span data-toggle="tooltip" data-placement="top" title="${data.supplier.name}">${data.no}</span>`;
        }
      },
      {
        "data": "inquiry_part.request_part.part.code"
      },
      {
        "data": "inquiry_part.request_part.part.name"
      },
      {
        "data": "inquiry_part.quantity"
      },
      {
        "data": "unit_price"
      },
      // { "data": "total_price_1" },
      {
        "data": "profit",
        render: function (data, type, row, meta) {
          return `<input type="number" name="profit" value="${data}" data-old="${data}" class="form-control select-search dt-editable" min="0.000" step="0.001">`;
        }
      },
      // { "data": "total_price_2" },
      {
        "data": "discount",
        render: function (data, type, row, meta) {
          return `<input type="number" name="discount" value="${data}" data-old="${data}" class="form-control select-search dt-editable" min="0.00" step="0.01">`;
        }
      },
      // { "data": "discount_value" },
      // { "data": "total_price_3" },
      {
        "data": "inquiry_part.availability_period"
      },
      {
        "data": "inquiry_part.availability",
        render: function (data, type, row, meta) {
          return data.name;
        }
      },
      {
        "data": "inquiry_part.quality",
        render: function (data, type, row, meta) {
          return data.name;
        }
      }
    ],
  });
} 

function updateQuotation(_data, _url, _form, _button = null) {
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

function addQuotation(_data, _url, _button = null) {
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
          addQuotationToPage(data);
          $(quotation_add_modal_selector).modal('hide');
          $(quotation_add_modal_selector).find(":input").val('');
          $(quotation_add_modal_selector).find("span.select2").remove();
          $(quotation_add_modal_selector).find("select").select2();
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    });
}

function addQuotationToPage(_data) {
  createQuotationTabHeader(_data.no);
  createQuotationTabBody(_data);
  $(tab_header_selector).find(`a[href='#${_data.no}']`).first().click();
}

function createQuotationTabHeader(_quotation_id) {
  let new_tab_header = $(tab_header_selector).find(".nav-item").first().clone();
  if (!new_tab_header.length) {
    location.reload();
  }
  let tab_header_anchor = new_tab_header.find("a").first();
  tab_header_anchor.removeClass("active");
  tab_header_anchor.attr("href", `#${_quotation_id}`);
  tab_header_anchor.html(_quotation_id);
  new_tab_header.insertBefore($(tab_header_selector).find("li").last());
}

function createQuotationTabBody(_data) {
  let new_tab_body = $(tab_body_selector).find("div").first().clone();
  let part_query_input = new_tab_body.find(part_query_input_selector).first();
  part_query_input.removeAttr("data-select2-id")
  part_query_input.removeAttr("last-search")
  // remove old datatable objects roughly
  new_tab_body.find(".table-responsive").first().html(new_tab_body.find(quotation_datatable_selector).first()[0].outerHTML)
  let table = new_tab_body.find(quotation_datatable_selector).first();
  let form = new_tab_body.find("form");
  table.removeAttr("id role aria-describedby");
  new_tab_body.find(":input").val('');
  fillForm(form, _data);
  new_tab_body.removeClass("active");
  new_tab_body.attr("id", `${_data.no}`);
  new_tab_body.attr("data-quotation-id", `${_data.id}`);
  new_tab_body.find("tbody").first().html("");
  new_tab_body.find(order_confirm_button_selector).first().removeAttr("hidden");
  new_tab_body.find(order_cancel_button_selector).first().attr("hidden", "");
  $(tab_body_selector).append(new_tab_body);
  new_tab_body.find("span.select2").remove();
  new_tab_body.find("select").select2();
  initializeAutoComplete(part_query_input, inquiry_parts_api_url, {
    "inquiry__project": project_id
  });
  initializeQuotationPartDatatables(table, quotation_parts_api_url, _data.id)
}

function createQuotationPart(_quotation_part_bulk_create_api_url, _table, _data, _button = null) {
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
    "save",
    () => {
      request
        .post_r(_quotation_part_bulk_create_api_url, _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
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
              console.log(errors)
              fire_alert([{ message: errors[0], icon: "error" }]);
            })
            throw new Error('Something went wrong');
          }
        });
    }
  );
}

function deleteQuotation(_quotation_id, _quotation_delete_api_url, _button = null) {
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
        .delete_r(_quotation_delete_api_url.replace("0", _quotation_id))
        .then((response) => {
          if (_button) {
            _button.html(button_text);
            _button.prop("disabled", false);
          }
          if (response.ok) {
            deleteQuotationFromPage(_quotation_id)
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

function deleteAllQuotationParts(_quotation_id, _quotation_part_bulk_delete_api_url, _table, _button = null) {
  let button_text = ""
  let inquiries = $(".inquiries");
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
        .delete_r(_quotation_part_bulk_delete_api_url.replace("0", _quotation_id))
        .then((response) => {
          if (_button) {
            _button.html(button_text);
            _button.prop("disabled", false);
          }
          if (response.ok) {
            inquiries.each(function (index, value) {
              $(value).prop('checked',false);
            });
            _table.ajax.reload();
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

function deleteQuotationFromPage(_quotation_id) {
  let quotation_tab = $(tab_body_selector).find(`div[data-quotation-id=${_quotation_id}]`).first();
  let quotation_no = quotation_tab.attr("id");
  let quotation_header = $(tab_header_selector).find(`a[href='#${quotation_no}']`).first().closest("li");
  quotation_header.remove();
  quotation_tab.remove(); 
  openCreateForm();
}

function orderConfirmation(_data, _url, _button = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  console.log(_data);
  request
    .post_r(_url, _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          let form = $(`[data-quotation-id=${data["quotation"]}]`).find('form').first();
          let confirm_button = form.find(order_confirm_button_selector).first();
          let cancel_button = form.find(order_cancel_button_selector).first();
          confirm_button.attr("hidden", "");
          cancel_button.removeAttr("hidden");
          $(order_confirmation_modal_selector).modal('hide');
          $(order_confirmation_modal_selector).find("input:not([type='checkbox'])").val('');
          $(order_confirmation_modal_selector).find('input:checkbox').removeAttr('checked');

        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    });
}

//cancel order confirm
function cancelOrderConfirmation(_order_confirmation_id, _order_confirmation_delete_api_url) {
  sweetCombineDynamic(
    "Are you sure?",
    "",
    "warning",
    "cancel",
    () => {
      request
        .delete_r(_order_confirmation_delete_api_url.replace("0", _order_confirmation_id))
        .then((response) => {
          if (response.ok) {
            let form = $(`[data-quotation-id=${_order_confirmation_id}]`).find('form').first();
            let confirm_button = form.find(order_confirm_button_selector).first();
            let cancel_button = form.find(order_cancel_button_selector).first();
            cancel_button.attr("hidden", "");
            confirm_button.removeAttr("hidden");
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

function initializeComparisonTable(_request_part_id, _filtered_inquiry_parts_api_url, _button = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  request
    .get_r(_filtered_inquiry_parts_api_url + `&request_part=${_request_part_id}`)
    .then((response) => {
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          buildComparisonTable(data);
        })
      } else {
        response.json().then(errors => {
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    })
}

function notConfirmedQuotationCreate(_data, _url, _button = null) {
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
          $(not_confirmed_quotation_modal_selector).modal('hide');
          location.reload();
        })
      } else {
        response.json().then(errors => {
          console.log(errors);
          fire_alert([{ message: errors, icon: "error" }]);
        })
        throw new Error('Something went wrong');
      }
    });
}


function buildAddInquiryTable(_data) {
  table = $(inquiry_add_part_datatable_selector);
  table.html('<tr id="inquiries" class="border-2 py-5"></tr>');
  var columns = [];
  var inq_columns = [];
  var addInquiryTableData = {}
  var cleanData = {}
  var column_counter=0;

  let inquiries = $("#inquiries");
  let inquiriesinnerhtml = `<th class="border-2">&nbsp</th><th class="border-2">&nbsp</th>`;
  
  tableElement =``;
  inquiries.html(inquiriesinnerhtml)

  $.each( _data, function( key, value ) {
    if (!inq_columns.includes(value.inquiry.no)){
      inq_columns.push(value.inquiry.no)
      inquiries.append(`<th class="border-2 text-center">${value.inquiry.no}</th>`);
      column_counter++;
    }
  });
  $.each( _data, function( key, value ) {
    addInquiryTableData[key] = {'part':value.request_part.part.name,'part_code':value.request_part.part.code,'unit_price':value.unit_price,'id':value.id,'is_added_in_quotation':value.is_added_in_quotation, 'availability_period':value.availability_period,'availability':value.availability.name,'currency':value.inquiry.currency.name,'inquiry_code':value.inquiry.no, 'supplier':value.inquiry.supplier.name }
  });
  $.each( addInquiryTableData, function( key, value ) {
    cleanData[value.part] = [];
    var arr = cleanData[value.part];
    var part = value.part;    

    $.each( addInquiryTableData, function( key, value ) {
      if(value.part == part){
      arr.push({'id':value.id,'part':value.part,'part_code':value.part_code,'unit_price':value.unit_price,'is_added_in_quotation':value.is_added_in_quotation, 'availability_period':value.availability_period,'availability':value.availability,'currency':value.currency, 'inquiry_code':value.inquiry_code,'supplier':value.supplier });
      }
    });
    
  });
  tableElement +=`<tr class="border-2 py-5"><th class="border-2">&nbsp</th><th class="border-2">&nbsp</th>`;
  $.each(addInquiryTableData,function(key,value){
    if(!columns.includes(value.supplier)){
      columns.push(value.supplier)
      tableElement +=`<th class="border-2 text-center">${value.supplier}</th>`;
    }
  });
  tableElement +=`</tr>`;


  $.each(cleanData,function(key,value){  
    tableElement +=`<tr class="border-2 py-5">`
    let counter = 0;
    $.each( value, function( key, value ) {
      if(counter==0){
        
        tableElement +=`<td class="border-2 text-center" id="${value.part}">${value.part}</td> <td class="border-2 text-center">${value.part_code}</td>`
        counter++;
      }

      
          
    });
    for( var cell = 1; cell<=column_counter; cell++){
       
      tableElement += `<td class="border-2 text-center" id="row"></td>`
  
    }
    tableElement +=`</tr>`
  });
  tableElement +=`</tr>`
  table.append(tableElement);

  var row_length=Object.keys(cleanData).length+2;
  $.each(cleanData,function(key,value){  
    $.each( value, function( key, value ) {
      
      
      var col_length = column_counter +2;
      var cell;
      for (var row_no=2; row_no<row_length; row_no++ ){
        for(var col_no=2; col_no<col_length; col_no++ ){
          var part_name = $('.inquiryAddPartElement tr:eq(' +row_no+ ') td:eq(0)').text();
          var inquiry_no = $('.inquiryAddPartElement tr:eq(0) th:eq('+col_no+')').text();
          
          cell=$('.inquiryAddPartElement tr:eq(' +row_no+ ') td:eq('+col_no+')');
           if(value.part ==part_name && value.inquiry_code == inquiry_no){
            if(value.is_added_in_quotation){
              
              cell.replaceWith( `<td class="border-2 text-center" id="row"><span class="px-1">${value.unit_price}&nbsp${value.currency}</span><span class="px-1">${value.availability_period}&nbsp${value.availability}</span>&nbsp<input type="checkbox" class="inquiries" id="${value.inquiry_code}" value="${value.id}" checked /></td>`);    
            }
            else{
              cell.replaceWith(`<td class="border-2 text-center" id="row"><span class="px-1">${value.unit_price}&nbsp${value.currency}</span><span class="px-1">${value.availability_period}&nbsp${value.availability}</span>&nbsp<input type="checkbox" class="inquiries" id="${value.inquiry_code}" value="${value.id}"  /></td>`);
            }
          } 
         
         
       }
      }
      
    }); 
  });



  tableElement =``;
  tableElement += `<tr><td class="border-2">&nbsp</td><td class="border-2">&nbsp</td>`
  for(var col_no=0; col_no<column_counter; col_no++){
    var inquiryCode = inq_columns[col_no]
    tableElement += `<td class="border-2 text-center">Select All &nbsp <input type="checkbox" class="inquiries" id="select_parts" onClick="selectParts()" data-inquiry-code="${inquiryCode}" value="undefined" /></td>`
  
  }
  tableElement += `</tr>`
  table.append(tableElement)
  var count_row =2;
  for(var col_no = 2; col_no<(column_counter+2); col_no++){
    for(var row_no = 2; row_no<row_length; row_no++){
      cell=$('.inquiryAddPartElement tr:eq(' +row_no+ ') td:eq('+col_no+')');
      if(cell.find('input:checkbox').is(":checked")){
        count_row++;
      }
    
  
      if(count_row == row_length){
        
        cell=$('.inquiryAddPartElement tr:eq(' +row_length+ ') td:eq('+col_no+')');
        cell.find('input:checkbox').prop('checked', true)
        console.log(cell)
      }
  }
    count_row =2;
  }

} 


function selectParts(){
  let select_parts=document.querySelectorAll("input[id=select_parts]");
  for(var count = 0; count< select_parts.length; count++){
    if(select_parts[count].checked){ 
      let inquiry_code=$(select_parts[count]).data("inquiry-code")
      let select_part_checkboxes=document.querySelectorAll("input[id="+inquiry_code+"]");
      for(var i=0; i< select_part_checkboxes.length; i++){
        select_part_checkboxes[i].checked=true;
      }
    }
    else{
      let inquiry_code=$(select_parts[count]).data("inquiry-code")
      let select_part_checkboxes=document.querySelectorAll("input[id="+inquiry_code+"]");
        for(var i=0; i< select_part_checkboxes.length; i++){
          select_part_checkboxes[i].checked=false;
        }
    
    }
  }
}

function buildComparisonTable(_data) {
  let currency_row = $("#comparison-currency")
  let inquiry_no_row = $("#comparison-inquiry-no")
  let supplier_name_row = $("#comparison-supplier-name")
  let prices_title_row = $("#comparison-prices-title")
  let part_results_row = $("#comparison-part-results")

  let currency_data = currency_row.find("td").first()
  let inquiry_no_data = inquiry_no_row.find("td").first()
  let supplier_name_data = supplier_name_row.find("td").first()
  let prices_title_data = prices_title_row.find("#td-price")[0].outerHTML

  let currency_row_innerHTML = ""
  let inquiry_row_innerHTML = ""
  let supplier_name_innerHTML = ""
  let prices_title_innerHTML = prices_title_data.repeat(_data.length)
  let part_results_innerHTML = `<td>${_data[0].request_part.part.name}</td>
                                <td>${_data[0].request_part.quantity}</td>
                                <td>${_data[0].request_part.part.unit.name}</td>`

  for (let inquiry_part of _data) {
    currency_row_innerHTML += currency_data.clone().html(inquiry_part.inquiry.currency.name)[0].outerHTML
    inquiry_row_innerHTML += inquiry_no_data.clone().html(inquiry_part.inquiry.no)[0].outerHTML
    supplier_name_innerHTML += supplier_name_data.clone().html(inquiry_part.inquiry.supplier.name)[0].outerHTML
    part_results_innerHTML += `<td colspan="2">${inquiry_part.unit_price}</td>`
  }

  currency_row.html(currency_row_innerHTML)
  inquiry_no_row.html(inquiry_row_innerHTML)
  supplier_name_row.html(supplier_name_innerHTML)
  prices_title_row.html(prices_title_innerHTML)
  part_results_row.html(part_results_innerHTML)

  $(part_comparison_modal_selector).modal();
}

function openCreateForm(){
  let $items = $('.tab-pane');
  let $button = $(add_new_tab_button_selector);
  if(!$items.length)
  { 
    $button.click();
  }
}
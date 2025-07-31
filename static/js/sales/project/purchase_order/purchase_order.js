//fetching 
const request = new Request(csrfToken);

const quotationPartsSelect = $("#quotation_parts_select")
const createPurchaseOrderForm = $("#create_purchase_order_form")
const save_stage_button_selector = ".save_stage";
const delete_stage_button_selector = ".delete_stage";
const purchase_order_datatable_selector = ".purchaseOrderDataTable";
const add_new_tab_button_selector = ".add-tab-button .text-success";

const purchase_order_pdf_button_selector = ".button-purchase-order-pdf";
const purchase_order_excel_button_selector =".button-purchase-order-excel";
$(document).ready(function(){
    openCreateForm();
});

$('#selectQuotationWithSelect').on('change', function () {
    // to remove old options
    quotationPartsSelect.find('option').remove()

    if (this.value) {
        updateQuotationParts(this.value)
    }
})

$('#tabBody').on("click", save_stage_button_selector, function () {
    let form = $('.tab-pane.active').find(".carousel-item.active").first().find('form').first()[0]
    let formData = new FormData(form);
    let purchase_order_id = $(form).closest(".carousel-item").attr("data-purchase-order-id");
    let data = Object.fromEntries(formData.entries());
    let button = $(this);
    updatePurchaseOrder(data, purchase_order_update_api_url.replace(0, purchase_order_id), $(this), button);
});

$(delete_stage_button_selector).on("click", function () {
    slider = $('.tab-pane.active').find(".carousel-item.active").attr("data-purchase-order-id");
    let purchase_order_id = slider
    deletePurchaseOrder(slider, purchase_order_update_api_url)

});

createPurchaseOrderForm.submit(function (event) {
    event.preventDefault();
    let quotation_parts = quotationPartsSelect.val();
    let button = $(this).find("button[type='submit']").first();
    createPurchaseOrder({
        "quotation_part": quotation_parts
    }, purchase_order_part_list_create_api_url, button);
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
        updatePart(part_id, purchase_order_part_update_api_url, data, table, null, button).then(() => {
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
    deletePart(part_id, purchase_order_part_update_api_url, table);
})

  //pdf and excel buttons listeners
  
  $(purchase_order_pdf_button_selector).on("click",function(){
    
    let table = $(purchase_order_datatable_selector).DataTable();
    console.log(table)
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(purchase_order_pdf_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate pdf file.", "warning");
    }
    else{
        let form = $('.tab-pane.active').find(".carousel-item.active").first().find('form').first()[0]
        let purchase_order_id = $(form).closest(".carousel-item").attr("data-purchase-order-id");
        if (purchase_order_id) {
            window.open(project_purchase_order_pdf_url.format(0, [project_id,purchase_order_id]), '_blank').focus()
        }
    }
  });
  $(purchase_order_excel_button_selector).on("click",function(){
  
    let table = $(purchase_order_datatable_selector).DataTable();
    table.ajax.reload( null, false );
    if(table.data().count()<1){
      $(purchase_order_excel_button_selector).removeAttr("href");
      sweetToastType("You should add part for generate excel file.", "warning");
    }
    else{
        let form = $('.tab-pane.active').find(".carousel-item.active").first().find('form').first()[0]
        let purchase_order_id = $(form).closest(".carousel-item").attr("data-purchase-order-id");
        if (purchase_order_id) {
            window.open(project_purchase_order_excel_url.format(0, [project_id,purchase_order_id]), '_blank').focus()
        }
    }
  });



setupDatatables();

//get request
function updateQuotationParts(quotation_id) {
    // add query parameters to the api url
    urlParams = new URLSearchParams();
    urlParams.set("quotation", quotation_id);
    quotation_parts_api_url.search = urlParams;

    request
        .get_r(quotation_parts_api_url).then((response) => {
            if (response.ok) {
                response.json().then(data => {
                    data.forEach((item) => {
                        let option = document.createElement("option")
                        option.innerHTML = [item.inquiry_part.inquiry.supplier.name, item.inquiry_part.request_part.part.code, item.inquiry_part.request_part.part.name].join(' / ')
                        option.value = item.id
                        quotationPartsSelect.append(option)
                    })
                })
            } else {
                response.json().then(errors => {
                    fire_alert([{ message: errors, icon: "error" }]);
                })
                throw new Error('Something went wrong');
            }
        });
}


//post request
function createPurchaseOrder(_data, _url, _button = null) {
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
                    location.reload();
                })
            } else {
                response.json().then(errors => {
                    fire_alert([{ message: errors, icon: "error" }]);
                })
                throw new Error('Something went wrong');
            }
        });
}

function updatePurchaseOrder(_data, _url, _form, _button = null) {
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
                })
            } else {
                response.json().then(errors => {
                    fire_alert([{ message: errors, icon: "error" }]);
                })
                throw new Error('Something went wrong');
            }
        });
}


function deletePurchaseOrder(_purchase_order_id, _purchase_order_delete_api_url) {

    sweetCombineDynamic(
        "Are you sure?",
        "You won't be able to revert this!",
        "warning",
        "delete",
        () => {
            request
                .delete_r(_purchase_order_delete_api_url.replace("0", _purchase_order_id))
                .then((response) => {
                    if (response.ok) {
                        // deleteQuotationFromPage(_quotation_id); 
                        location.reload();
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

function setupDatatables() {
    $.each($(purchase_order_datatable_selector), function () {
        let purchase_order_id = $(this).closest(".carousel-item").attr("data-purchase-order-id");
        console.log(purchase_order_id)
        initializePurchaseOrderPartDatatables($(this), purchase_order_parts_api_url, purchase_order_id);
    });
}

function initializePurchaseOrderPartDatatables(_table, _purchase_order_parts_api_url, _purchase_order_id) {
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
        },
        "searchCols": [
            null,
            null,
            null,
            {
                "search": _purchase_order_id
            },
        ],
        "serverSide": true,
        "ajax": _purchase_order_parts_api_url,
        "columns": [
            {
                "data": "id"
            },
            {
                "data": "quotation_part.inquiry_part.request_part.part.code"
            },
            {
                "data": "quotation_part.inquiry_part.request_part.part.name"
            },
            {
                "data": "purchase_order.id"
            },
            {
                "data": "quotation_part.inquiry_part.quantity"
            },
            {
                "data": "quotation_part.inquiry_part.request_part.part.unit.name"
            },
            {
                "data": "unit_price"
            },
            {
                "data": "total_price_3"
            },
            {
                "data": "order_type",
                render: function (data, type, row, meta) {
                    let select_element = `<select name="order_type" class="form-control dt-editable" data-old="${data.value}">`
                    for (const [key, value] of Object.entries(order_type_choices)) {
                        let selected = (key == data.value) ? 'selected' : ''
                        select_element += `<option value="${key}" ${selected}>${value}</option>`
                    }
                    select_element += `</select>`
                    return select_element;
                }
            },
            {
                "data": "quotation_part.inquiry_part.availability_period"
            },
            {
                "data": "quotation_part.inquiry_part.availability", // these are not because of database design, we need both display name and the value
                render: function (data, type, row, meta) {
                    return data.name; // custom return, actual data {availability:week}, custom data {availability:{name:Week,value:week}}
                }
            },
            {
                "data": "quotation_part.inquiry_part.quality",
                render: function (data, type, row, meta) {
                    return data.name;
                }
            }
        ],
        "columnDefs": [
            {
                searchable: false,
                targets: [7],
            },
            {
                orderable: false,
                targets: [7],
            },
            {
                "targets": 12,
                "data": null,
                className: 'align-center',
                createdCell: function (td, cellData, rowData, row, col) {
                    $(td).css('white-space', 'nowrap');
                },
                defaultContent: `
                    <button class='partUpdate btn p-0 mx-1'><i class='text-success icon-checkmark3'></i></button>
                    <button class='partDelete btn p-0 mx-1'><i class='text-danger fas fa-trash'></i></button>`
            },
            {
                targets: [0, 3],
                className: "d-none"
            }
        ]
    });
}

function openCreateForm(){
    let $items = $('.tab-pane');
    let $button = $(add_new_tab_button_selector);
    if(!$items.length)
    { 
      $button.click();
    }
}
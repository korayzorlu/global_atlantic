const request = new Request(csrfToken);
const claims_follow_up_start_form = $("#claims_follow_up_start_form");
const createDeliveryForms = $("#modal_delivery_add").find("form")
const save_stage_button_selector = ".save_stage";
const delivered_button_selector = ".deliver_stage";
const delete_stage_button_selector = ".delete_stage";
const delivery_delete_button_selector = ".deliveryDelete"
const tab_body_selector = "#tabBody"
const tab_header_selector = "#tabHeader";
const purchaseOrderSelectSelector = "[name=purchase_order]"
const insuranceModalSelector = "#modal_insurance_add"
const transportationModalSelector = "#modal_transportation_add"
const taxModalSelector = "#modal_tax_add"
const customsModalSelector = "#modal_customs_add"
const packingModalSelector = "#modal_packing_add"
const claimFollowUpModalSelector = "#modal_claim_follow_up"
const purchaseOrderPartsSelectSelector = "[name=parts]"
const reason_choices_selector = "select[name=claim_reason_choices]"
const add_new_tab_button_selector = ".add-tab-button .text-success";


const fillForm = function (_form, _data) {
    $.each(_data, function (key, value) {
        _form.find(`[name='${key}']`).first().val(value).trigger('change');
    });
}

$(document).ready(function(){
    openCreateForm();
});

createDeliveryForms.on("submit", function (event) {
    event.preventDefault();
    let formData = new FormData(this);
    let process_type = $(this).closest(".tab-pane").attr('data-type')
    formData.append("project", project_id);
    formData.append("process_type", process_type);
    let data = Object.fromEntries(formData.entries());
    data["parts"] = $(this).find("[name=parts]").first().val();
    let button = $(this).find("button[type='submit']").first();
    createDelivery(data, delivery_create_api_url, button);
});

$('#tabHeader').on("click", delivery_delete_button_selector, function () {
    let current_tab_header = $(this).closest(".nav-item");
    let current_tab_body_selector = current_tab_header.find("a").first().attr("href");
    let current_tab_body = $(tab_body_selector).find(current_tab_body_selector).first();
    let delivery_id = current_tab_body.attr("data-delivery-id");
    deleteDelivery(delivery_id, delivery_update_api_url);
});

//delivery modal js 
$(purchaseOrderSelectSelector).each(function () {
    let partsElement = $(this).closest("form").find("[name=parts]").first();
    partsElement.find('option').remove();
})

$(tab_body_selector).on('change', purchaseOrderPartsSelectSelector, function () {
    let delivery_id = $(this).closest('.tab-pane.active').attr("data-delivery-id");
    let table = $(this).closest('.card').first().find("table").first()
    if (this.value) {
        addPart({ delivery: delivery_id, purchase_order_part: this.value }, delivery_part_add_api_url, table)
    }
})

$(purchaseOrderSelectSelector).on('change', function () {
    // to remove old options
    let partsElement = $(this).closest("form").find("[name=parts]").first();
    partsElement.find('option').remove();
    if (this.value) {
        refreshPurchaseOrderParts(this.value, purchase_order_parts_api_url, partsElement)
    }
})


$(save_stage_button_selector).on('click', function () {
    let form = $(this).closest(".tab-pane").find("form")[0]
    if (form.reportValidity()) {
        let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
        let formData = new FormData(form);
        let data = Object.fromEntries(formData.entries());
        updateDeliveryWithMail(delivery_id, data, delivery_update_api_url);
    }
})

$(delivered_button_selector).on('click', function () {
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let data = { 'is_delivered': true }
    let button = $(this);
    deliverDelivery(delivery_id, delivery_update_api_url, data, button);
})

//part list data

$('.part-list-table').each(function () {
    let delivery_id = $(this).closest('.tab-pane').attr("data-delivery-id");
    refreshDeliveryParts(delivery_id, delivery_api_url, $(this));
})

$('.part-list-table').on("click", ".partDelete", function () {
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let part_id = $(this).closest("tr").find("td").first().html()
    let table = $(this).closest("table")
    let button = $(this)
    console.log(delivery_id, part_id)
    deletePart(delivery_id, part_id, delivery_part_remove_api_url, table)
});


$('.transportation-btn').on("click", function () {
    let delivery_id = $(this).closest(".tab-pane").attr("data-delivery-id");
    getCostData(delivery_id, delivery_transportation_api_url).then((data) => {
        let modal = $(transportationModalSelector);
        modal.modal();
        if (data.currency) {
            data.currency = data.currency.id;
        } else {
            data.currency = null;
        }
        fillForm(modal.find("form").first(), data);
    })
})

$('.tax-btn').on("click", function () {
    let delivery_id = $(this).closest(".tab-pane").attr("data-delivery-id");
    getCostData(delivery_id, delivery_tax_api_url).then((data) => {
        let modal = $(taxModalSelector);
        modal.modal();
        if (data.currency) {
            data.currency = data.currency.id;
        } else {
            data.currency = null;
        }
        fillForm(modal.find("form").first(), data);
    })
})

$('.insurance-btn').on("click", function () {
    let delivery_id = $(this).closest(".tab-pane").attr("data-delivery-id");
    getCostData(delivery_id, delivery_insurance_api_url).then((data) => {
        let modal = $(insuranceModalSelector);
        modal.modal();
        if (data.currency) {
            data.currency = data.currency.id;
        } else {
            data.currency = null;
        }
        fillForm(modal.find("form").first(), data);
    })
})

$('.customs-btn').on("click", function () {
    let delivery_id = $(this).closest(".tab-pane").attr("data-delivery-id");
    getCostData(delivery_id, delivery_customs_api_url).then((data) => {
        let modal = $(customsModalSelector);
        modal.modal();
        if (data.currency) {
            data.currency = data.currency.id;
        } else {
            data.currency = null;
        }
        fillForm(modal.find("form").first(), data);
    })
})

$('.packing-btn').on("click", function () {
    let delivery_id = $(this).closest(".tab-pane").attr("data-delivery-id");
    getCostData(delivery_id, delivery_packing_api_url).then((data) => {
        let modal = $(packingModalSelector);
        modal.modal();
        if (data.currency) {
            data.currency = data.currency.id;
        } else {
            data.currency = null;
        }
        fillForm(modal.find("form").first(), data);
    })
})

$(transportationModalSelector).find("form").first().on("submit", function (event) {
    event.preventDefault();
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    let modal = $(this).closest(".modal");
    let button = $(this).find("button[type='submit']").first();
    updateDeliveryData(delivery_id, data, delivery_transportation_update_api_url, modal, button, function () { refreshCosts(delivery_id) });
})

$(taxModalSelector).find("form").first().on("submit", function (event) {
    event.preventDefault();
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    let modal = $(this).closest(".modal");
    let button = $(this).find("button[type='submit']").first();
    updateDeliveryData(delivery_id, data, delivery_tax_update_api_url, modal, button, function () { refreshCosts(delivery_id) });
})

$(insuranceModalSelector).find("form").first().on("submit", function (event) {
    event.preventDefault();
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    let modal = $(this).closest(".modal");
    let button = $(this).find("button[type='submit']").first();
    updateDeliveryData(delivery_id, data, delivery_insurance_update_api_url, modal, button, function () { refreshCosts(delivery_id) });
})

$(customsModalSelector).find("form").first().on("submit", function (event) {
    event.preventDefault();
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    let modal = $(this).closest(".modal");
    let button = $(this).find("button[type='submit']").first();
    updateDeliveryData(delivery_id, data, delivery_customs_update_api_url, modal, button, function () { refreshCosts(delivery_id) });
})

$(packingModalSelector).find("form").first().on("submit", function (event) {
    event.preventDefault();
    let delivery_id = $(tab_body_selector).find('.tab-pane.active').attr("data-delivery-id");
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    let modal = $(this).closest(".modal");
    let button = $(this).find("button[type='submit']").first();
    updateDeliveryData(delivery_id, data, delivery_packing_update_api_url, modal, button, function () { refreshCosts(delivery_id) });
})

refreshCosts() //to call refreshCosts function 

//post request
function createDelivery(_data, _url, _button = null) {
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

function deliverDelivery(_delivery_id, _delivery_update_api_url, _data, _button) {
    sweetCombineDynamic(
        "Are you sure?",
        "You won't be able to make any changes!",
        "warning",
        "deliver",
        () => {
            request
                .patch_r(_delivery_update_api_url.replace("0", _delivery_id), _data)
                .then((response) => {
                    if (response.ok) {
                        _button.attr("disabled", '')
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

//delivery tab delete js 
function deleteDelivery(_delivery_id, _delivery_delete_api_url, _button = null) {
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
                .delete_r(_delivery_delete_api_url.replace("0", _delivery_id))
                .then((response) => {
                    if (_button) {
                        _button.html(button_text);
                        _button.prop("disabled", false);
                    }
                    if (response.ok) {
                        deleteDeliveryFromPage(_delivery_id);
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

function deleteDeliveryFromPage(_delivery_id) {
    let delivery_tab = $(tab_body_selector).find(`div[data-delivery-id=${_delivery_id}]`).first();
    let delivery_no = delivery_tab.attr("id");
    let delivery_header = $(tab_header_selector).find(`a[href='#${delivery_no}']`).first().closest("li");
    delivery_header.remove();
    delivery_tab.remove();
    openCreateForm();
}

function refreshCosts(delivery_id = null) {
    let delivery_list = [];
    if (delivery_id) {
        delivery_list = $(`[data-delivery-id=${delivery_id}]`);
    } else {
        delivery_list = $(tab_body_selector).find('.tab-pane');
    }

    delivery_list.each(function () {
        let delivery_tab = $(this)
        getDeliveryData(delivery_tab.attr('data-delivery-id'), delivery_api_url).then((data) => {
            delivery_tab.find('.costs').each(function () {
                let child = $(this).find('div').first();
                let cost_name = child.attr('class');
                let total_charged_amount_element = child.find('.total-charged-amount').first();
                let cost_currency_element = child.find('.cost-currency').first();
                total_charged_amount_element.html(data[cost_name].total_charged_amount)
                if (data[cost_name].currency) {
                    cost_currency_element.html(data[cost_name].currency.name)
                } else {
                    cost_currency_element.html("---")
                }
            })
        })
    })
}

function getDeliveryData(_delivery_id, _delivery_api_url) {
    return new Promise((resolve, reject) => {
        request
            .get_r(_delivery_api_url.replace('0', _delivery_id)).then((response) => {
                if (response.ok) {
                    response.json().then(data => {
                        resolve(data);
                    })
                } else {
                    response.json().then(errors => {
                        fire_alert([{ message: errors, icon: "error" }]);
                        reject();
                    })
                    throw new Error('Something went wrong');
                }
            });
    })
}

function getCostData(_delivery_id, _delivery_cost_url) {
    return new Promise((resolve, reject) => {
        request
            .get_r(_delivery_cost_url.replace('0', _delivery_id)).then((response) => {
                if (response.ok) {
                    response.json().then(data => {
                        resolve(data);
                    })
                } else {
                    response.json().then(errors => {
                        fire_alert([{ message: errors, icon: "error" }]);
                        reject();
                    })
                    throw new Error('Something went wrong');
                }
            });
    })
}

function updateDeliveryData(_delivery_id, _data, _url, _modal = null, _button = null, _callback = null) {
    let button_text = ""
    if (_button) {
        button_text = _button.html();
        _button.prop("disabled", true);
        _button.html(`<i class="icon-spinner2 spinner"></i>`);
    }
    request
        .patch_r(_url.replace(0, _delivery_id), _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
            if (_button) {
                _button.html(button_text);
                _button.prop("disabled", false);
            }
            if (response.ok) {
                response.json().then(data => {
                    if (_modal) {
                        _modal.modal('hide');
                    }
                    if (_callback) {
                        _callback()
                    }
                })
            } else {
                response.json().then(errors => {
                    fire_alert([{ message: errors, icon: "error" }]);
                })
                throw new Error('Something went wrong');
            }
        });
}

function updateDeliveryWithMail(_delivery_id, _data, _url, _callback = null) {
    Swal.fire({
        title: 'Do you want to send the mail to the person in contact of the customer?',
        icon: 'question',
        showCancelButton: true,
        showDenyButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes',
        denyButtonText: 'No',
        customClass: {
            confirmButton: "btn btn-primary",
            denyButton: "btn btn-light",
            cancelButton: "btn btn-light",
        },
    }).then((result) => {
        if (result.isConfirmed) {
            _data.send_mail = "on"
        }
        if (!result.isCancelled) {
            request
                .patch_r(_url.replace(0, _delivery_id), _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
                    if (response.ok) {
                        response.json().then(data => {
                            if (_callback) {
                                _callback()
                            }
                        })
                    } else {
                        response.json().then(errors => {
                            fire_alert([{ message: errors, icon: "error" }]);
                        })
                        throw new Error('Something went wrong');
                    }
                });
        }
    })
}

function refreshPurchaseOrderParts(purchase_order_id, purchase_order_parts_api_url, purchase_order_parts_select) {
    // add query parameters to the api url
    urlParams = new URLSearchParams();
    urlParams.set("purchase_order", purchase_order_id);
    purchase_order_parts_api_url.search = urlParams;

    request
        .get_r(purchase_order_parts_api_url).then((response) => {
            if (response.ok) {
                response.json().then(data => {
                    data.forEach((item) => {
                        let option = document.createElement("option")
                        option.innerHTML = item.str
                        option.value = item.id
                        purchase_order_parts_select.append(option)
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

//part list data js below

function addPart(_data, _url, _table, _button = null) {
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
                    refreshDeliveryParts(data.delivery, delivery_api_url, _table)
                })
            } else {
                response.json().then(errors => {
                    fire_alert([{ message: errors, icon: "error" }]);
                })
                throw new Error('Something went wrong');
            }
        });
}

function deletePart(_delivery_id, _part_id, _delivery_part_remove_api_url, _table, _button = null) {
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
                .delete_r(_delivery_part_remove_api_url.format(0, [_delivery_id, _part_id]))
                .then((response) => {
                    if (_button) {
                        _button.html(button_text);
                        _button.prop("disabled", false);
                    }
                    if (response.ok) {
                        refreshDeliveryParts(_delivery_id, delivery_api_url, _table)
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

function refreshDeliveryParts(_delivery_id, _delivery_api_url, _table) {
    let table_body = _table.find('tbody')[0]
    table_body.innerHTML = `<tr class="text-center"><td colspan=3><i class="icon-spinner2 spinner"></i></td></tr>`;
    request
        .get_r(_delivery_api_url.replace(0, _delivery_id)).then((response) => {
            if (response.ok) {
                response.json().then(data => {

                    table_body.innerHTML = ""
                    data.parts.forEach((part) => {
                        let row = document.createElement("tr")
                        row.innerHTML = `
                        <td class="d-none">${part.id}</td>
                        <td>${part.quotation_part.inquiry_part.request_part.part.code}</td>
                        <td>
                        <a href="${part_detail_url.replace(0, part.quotation_part.inquiry_part.request_part.part.id)}"
                        class="text-default font-weight-semibold letter-icon-title" target="blank">
                        ${part.quotation_part.inquiry_part.request_part.part.name}</a>
                        </td>
                        <td>
                        <button onmouseover="changeColor(this)" onmouseout="colorBack(this)" class="partDelete btn">
                        <i class="fas fa-trash"></i>
                        </button>
                        </td>
                        `
                        table_body.innerHTML += row.outerHTML;
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


/* claims follow up open modal */
function claimsFollowUpCreate(_data, _url, _button = null) {
    let button_text = ""
    if (_button) {
      button_text = _button.html();
      _button.prop("disabled", true);
      _button.html(`<i class="icon-spinner2 spinner"></i>`);
    }
    request
      .post_r(_url, _data).then((response) => { 
        if (_button) {
          _button.html(button_text);
          _button.prop("disabled", false);
        }
        if (response.ok) {
          response.json().then(data => {
            $(claimFollowUpModalSelector).modal('hide');
            window.location = claim_detail_url.replace(0, data.id);
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


claims_follow_up_start_form.submit(function (event){
    event.preventDefault();
    let formData = new FormData(this);
    
    let delivery_id = $("#tabBody .tab-pane.active").data('delivery-id');
    
    formData.append("delivery", delivery_id);
    let data = Object.fromEntries(formData.entries());
    let claim_reason_choices = $(reason_choices_selector).val();
    data.claim_reason_choices=claim_reason_choices;
    console.log(data);
    let button = $(this).find("button[type='submit']").first();
    claimsFollowUpCreate(data, claims_follow_up_create_api_url, button);
    
  })

function openCreateForm(){
    let $items = $('.tab-pane');
    let $button = $(add_new_tab_button_selector);
    if($items.length < 11)
    { 
      $button.click();
    }
}
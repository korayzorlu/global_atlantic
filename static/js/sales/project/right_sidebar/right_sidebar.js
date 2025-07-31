const file_add_input = $("#file-add");
const file_table = $("#file-table");
const file_delete_button_selector = ".fileDelete";
const finish_button_selector = ".finish_project";
const responsible_select_selector = "[name=responsible-select]";

refreshFileData(project_documents_api_url, file_table)
    .catch((errors) => {
        fire_alert([{ message: errors, icon: "error" }]);
    });

file_add_input.on("change", function () {
    if (this.files && this.files[0]) {
        uploadFile(this.files[0], project_id, project_document_create_api_url, file_add_input.closest('.btn').find('span'))
            .then((data) => {
                refreshFileData(project_documents_api_url, file_table)
                    .catch((errors) => {
                        fire_alert([{ message: errors, icon: "error" }]);
                    });
            })
            .catch((errors) => {
                fire_alert([{ message: errors, icon: "error" }]);
            })
        this.value = '';
    }
})



file_table.on("click", file_delete_button_selector, function () {
    let file_id = $(this).closest("tr").find("td").first().html()
    deleteFile(file_id, project_document_update_api_url)
        .then(() => {
            refreshFileData(project_documents_api_url, file_table)
                .catch((errors) => {
                    fire_alert([{ message: errors, icon: "error" }]);
                });
        })
        .catch((errors) => {
            fire_alert([{ message: errors, icon: "error" }]);
        })
})

$(responsible_select_selector).on('change', function () {
    let element = this
    if (this.tagName == 'SELECT') element = $(this).closest('tr').find(`[aria-labelledby*=${this.name}]`)[0] // because of select2

    if ($(this).attr("data-old") != this.value) {
        element.classList.add("border-danger");
        if (this.value) {
            updateResponsible(project_id, { 'responsible': this.value }, project_update_api_url)
                .then(() => {
                    $(this).attr("data-old", this.value);
                    $(this).trigger("change");
                })
                .catch((errors) => {
                    fire_alert([{ message: errors, icon: "error" }]);
                })
        }
    } else {
        element.classList.remove("border-danger");
    }
})

//finish button is below
$(finish_button_selector).on('click', function () {
    let data = { 'is_closed': true }
    let button = $(this);
    projectFinish(project_id, project_update_api_url, data, button)
        .then(() => {
            button.attr("disabled", '');
        })
        .catch((errors) => {
            fire_alert([{ message: errors, icon: "error" }]);
        })
})

function uploadFile(_file, _project_id, _url, _button, _modal) {
    return new Promise((resolve, reject) => {
        let formData = new FormData()
        let button_text = ""
        if (_button) {
            button_text = _button.html();
            _button.prop("disabled", true);
            _button.html(`<i class="icon-spinner2 spinner"></i>`);
        }
        formData.append('file', _file)
        formData.append('project', _project_id)
        request
            .post_file(_url, formData).then((response) => {
                if (_button) {
                    _button.html(button_text);
                    _button.prop("disabled", false);
                }
               
                if (response.ok) {
                    response.json().then(data => {
                        if (_modal) {
                            _modal.modal('hide');
                        }
                        resolve(data)
                    })
                } else {
                    response.json().then(errors => {
                        reject(errors);
                    })
                }
            })
    })
};

function deleteFile(_file_id, _url) {
    return new Promise((resolve, reject) => {
        sweetCombineDynamic(
            "Are you sure?",
            "You won't be able to revert this!",
            "warning",
            "delete",
            () => {
                request
                    .delete_r(_url.replace(0, _file_id))
                    .then((response) => {
                        if (response.ok) {
                            resolve()
                        } else {
                            response.json().then(errors => {
                                reject(errors)
                            })
                        }
                    })
            }
        );
    });
}


//function for imprint button ,when click on it,table data will be refreshed
$(function() {
    $('.overViewBTN').click(function() {
      refreshFileData(project_documents_api_url,file_table)

    });
  });

function refreshFileData(_url, _table) {
    return new Promise((resolve, reject) => {
        let table_body = _table.find('tbody')[0]
        table_body.innerHTML = `<tr class="text-center"><td colspan=3><i class="icon-spinner2 spinner"></i></td></tr>`;
        request
            .get_r(_url).then((response) => {
                if (response.ok) {
                    response.json().then(data => {
                        table_body.innerHTML = ""
                        data.forEach((file) => {
                            let row = document.createElement("tr")
                            row.innerHTML = `
                            <td class="d-none p-1">${file.id}</td>
                            <td class="p-1">
                            <a href="${file.file}" title="${file.filename}"
                            class="font-weight-semibold" target="blank">
                            <div>${file.filename}</div>
                            </a>
                            </td>
                            <td class="p-1">${file.size}</td>
                            <td class="p-1">${file.created_at}</td>
                            ` 
                            let button_remove = `
                            <td class="p-1">
                            <button class="fileDelete btn">
                            <i class="fas fa-trash"></i>
                            </button>
                            </td>
                            `
                            if(typeof claim == 'undefined') row.innerHTML += button_remove
                            table_body.innerHTML += row.outerHTML;
                        })
                        resolve();
                    })
                } else {
                    response.json().then(errors => {
                        reject(errors);
                    })
                }
            })
    });
}

function updateResponsible(_project_id, _data, _url) {
    return new Promise((resolve, reject) => {
        request
            .patch_r(_url.replace(0, _project_id), _data).then((response) => { // https://stackoverflow.com/a/38236296/14506165
                if (response.ok) {
                    response.json().then(data => {
                        resolve(data);
                    })
                } else {
                    response.json().then(errors => {
                        reject(errors);
                    })
                }
            });
    });
}

function projectFinish(_project_id, _project_update_api_url, _data) {
    return new Promise((resolve, reject) => {
        sweetCombineDynamic(
            "Are you sure?",
            "You won't be able to make any changes!",
            "warning",
            "finish",
            () => {
                Swal.fire({
                    title: 'Please enter your notes',
                    input: 'text',
                    inputAttributes: {
                        autocapitalize: 'off'
                    },
                    showCancelButton: true,
                    confirmButtonText: 'Send',
                    showLoaderOnConfirm: true,
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-light",
                        denyButton: "btn btn-light",
                        input: "form-control",
                    },
                    preConfirm: (login) => {
                        _data.close_notes = login
                        return request
                            .patch_r(_project_update_api_url.replace("0", _project_id), _data)
                            .then((response) => {
                                if (response.ok) {
                                    resolve();
                                } else {
                                    response.json().then(errors => {
                                        reject(errors);
                                    })
                                }
                            })
                    },
                    allowOutsideClick: () => !Swal.isLoading()
                })
            }
        );
    });
}

const request = new Request(csrfToken);
const claims_follow_up_update_form=$("#claim_follow_up_result_form");
const claimFollowUpModalSelector = "#modal_claim_follow_up_update_modal"
const claim_result_choice_selector="select[name=claim_results]"

function claimsFollowUpUpdate(_claim_id, _data, _url, _modal = null, _button = null, _callback = null) {
  let button_text = ""
  if (_button) {
    button_text = _button.html();
    _button.prop("disabled", true);
    _button.html(`<i class="icon-spinner2 spinner"></i>`);
  }
  request
    .patch_r(_url.replace(0, _claim_id), _data).then((response) => { 
      if (_button) {
        _button.html(button_text);
        _button.prop("disabled", false);
      }
      if (response.ok) {
        response.json().then(data => {
          console.log(data);
          $(claimFollowUpModalSelector).modal('hide');
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


claims_follow_up_update_form.submit(function (event){
  event.preventDefault();
  let modal = $(this).closest(".modal");
  let button = $(this).find("button[type='submit']").first();
  let claim_id = $('#update-claim').attr("value");
  let formData = new FormData(this);
  let data = Object.fromEntries(formData.entries());
  let claim_result_choices = $(claim_result_choice_selector).val();
  data.claim_results=claim_result_choices;
  console.log(claim_result_choices);
  claimsFollowUpUpdate(claim_id, data, claim_update_api_url, modal, button);
})
/* 
refreshCosts() */

/* function claimsFollowUpUpdate(_data, _url, _button = null) {
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
            console.log(data);
            $(claimFollowUpModalSelector).modal('hide');
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

  
  claims_follow_up_update_form.submit(function (event){
    event.preventDefault();
    let formData = new FormData(this);
    let data = Object.fromEntries(formData.entries());
    let claim_result_choices = $(claim_result_choice_selector).val();
    data.claim_result=claim_result_choices;
    console.log(data);
    let button = $(this).find("button[type='submit']").first();
    claimsFollowUpUpdate(data, claims_follow_up_update_api,  button);
  })
 */

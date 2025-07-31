// // Variables
// const inputSwitchery = document.getElementById("companyGroupControl");
// const selectCompanyGroup = document.getElementById("id_company_group");
// const formGroup = selectCompanyGroup.closest(".form-group");

// sales_team_input = $("select[name='sales_team']");
// customer_representative_input = $("select[name='customer_representative']");
// country_input = $("select[name='country']");
// city_input = $("select[name='city']");

// const cleanOptions = function (select_input) {
//   select_input.find("option").each(function () {
//     $(this).removeAttr("selected");
//     $(this).removeAttr("data-select2-id");
//     if ($(this).val()) {
//       $(this).remove();
//     }
//   });
// };

// const fillOptions = function (select_input, data, show_key, callback = null) {
//   // get already selected value
//   // to select it with new option list
//   let values = getSelection(select_input);

//   cleanOptions(select_input);
//   dom_element = select_input.get(0);

//   for (option of data) {
//     selected =
//       values && values.includes(option.id.toString()) ? "selected" : "";
//     dom_element.innerHTML += `<option value="${option.id}" ${selected}>${option[show_key]}</option>`;
//   }
//   if (callback) {
//     callback();
//   }
// };

// const getSelection = function (select_input) {
//   let values = select_input.val();
//   if (values) {
//     return values;
//   } else {
//     return null;
//   }
// };

// // const getFullName = function (data) {
// //     full_name = [data.first_name, data.last_name].join(' ');
// //     full_name_with_username = `${full_name} (${data.username})`;
// //     return full_name_with_username;
// // }

// init();

// function init() {
//   updateUsers();
//   updateCities();
//   setupListeners();
// }

// function setupListeners() {
//   sales_team_input.change(updateUsers);
//   country_input.change(updateCities);
// }

// function updateUsers() {
//   new_value = getSelection(sales_team_input);
//   if (!new_value) {
//     cleanOptions(customer_representative_input);
//   } else {
//     urlParams = new URLSearchParams();
//     urlParams.set("team", new_value);
//     users_api_url.search = urlParams;
//     fetch(users_api_url)
//       .then((response) => response.json())
//       .then((data) =>
//         fillOptions(
//           customer_representative_input,
//           data,
//           (show_key = "username")
//         )
//       );
//   }
// }

// function updateCities() {
//   new_value = getSelection(country_input);
//   if (!new_value) {
//     cleanOptions(city_input);
//   } else {
//     urlParams = new URLSearchParams();
//     urlParams.set("country", new_value);
//     cities_api_url.search = urlParams;
//     fetch(cities_api_url)
//       .then((response) => response.json())
//       .then((data) => fillOptions(city_input, data, (show_key = "name")));
//   }
// }

// if (selectCompanyGroup.value != "") {
//   formGroup.style.display = "block";
//   $(selectCompanyGroup).prop("disabled", false);
//   inputSwitchery.setAttribute("checked", true);
// } else {
//   $(selectCompanyGroup).prop("disabled", true);
//   formGroup.style.display = "none";
// }

// // Group eklemej için gereken fonksiyon.
// //Back endden gelen selectlerde default olarak select2 classını olduğundan silmek gerekiyor.
// async function addGroup() {
//   $("#id_company_group").removeClass("select-search");
// }

// addGroup().then(() => {
//   $("#id_company_group").select2({
//     tags: true
//   });
// });

// // Input switch control

// inputSwitchery.onclick = changeInputsState;
// function changeInputsState() {
//   if (this.checked) {
//     $(selectCompanyGroup).prop("disabled", false);
//     formGroup.style.display = "block";
//     sweetToastType("You can select Company group.", "success");
//   } else {
//     $(selectCompanyGroup).prop("disabled", true);
//     formGroup.style.display = "none";
//     sweetToastType("Open group switch to select Company group.", "warning");
//   }
// }

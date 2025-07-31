// // Defaults
// var swalInit = swal.mixin({
//   buttonsStyling: false,
//   customClass: {
//     confirmButton: "btn btn-primary",
//     cancelButton: "btn btn-light",
//     denyButton: "btn btn-light",
//     input: "form-control",
//   },
// });

// // === BASIC ===

// // ---Alert message -- notification type
// function sweetType(title, text, type) {
//   swalInit.fire({
//     title: title,
//     text: text,
//     icon: type,
//   });
// }

// // Combine messages
// // ---Message with a function attached to the "Confirm" and "Cancel" buttons
// function sweetCombine(
//   title,
//   text,
//   type,
//   action,
//   success,
//   succesMessageTitle,
//   succesMessageText,
//   succesMessageType,
//   error,
//   errorMessageTitle,
//   errorMessageText,
//   errorMessageType
// ) {
//   swalInit
//     .fire({
//       title: title,
//       text: text,
//       icon: type,
//       showCancelButton: true,
//       confirmButtonText: "Yes, " + action + " it!",
//       cancelButtonText: "No, cancel!",
//       confirmButtonClass: "btn btn-success",
//       cancelButtonClass: "btn btn-danger",
//       buttonsStyling: false,
//     })
//     .then(function (result) {
//       if (result.value) {
//         swalInit.fire(succesMessageTitle, succesMessageText, succesMessageType);
//         success();
//       } else if (result.dismiss === swal.DismissReason.cancel) {
//         swalInit.fire(errorMessageTitle, errorMessageText, errorMessageType);
//         error();
//       }
//     });
// }

// // === TOASTS ===

// // ---Alert message -- toasts type
// function sweetToastType(text, type) {
//   swalInit.fire({
//     text: text,
//     icon: type,
//     toast: true,
//     showConfirmButton: false,
//     timer: 4000,
//     position: "bottom-right",
//   });
// }
// // === INPUTS ===

// // ---Alert message -- toasts type
// function sweetInputType(title, type, placeholder, rensponseType, responseHTML) {
//   swalInit
//     .fire({
//       title: title,
//       input: type,
//       inputPlaceholder: placeholder,
//       showCancelButton: true,
//       inputClass: "form-control",
//     })
//     .then(function (result) {
//       if (result.value) {
//         swalInit.fire({
//           type: rensponseType,
//           html: responseHTML,
//           //   html: "Hi, " + result.value,
//         });
//       }
//     });
// }

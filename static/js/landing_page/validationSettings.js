export let formValidation = function () {
  $(".form-validate").validate({
    errorClass: "error-message",
    successClass: "success-message",
    validClass: "validation-valid-label",

    highlight: function (element, errorClass) {
      $(element).removeClass(errorClass);
      $(element).addClass("error-input");
    },
    unhighlight: function (element, errorClass) {
      $(element).removeClass(errorClass);
      $(element).removeClass("error-input");
    },
    success: function (label) {
      label.addClass("validation-success").text(""); // remove to hide Success message
    },

    rules: {
      username: {
        rangelength: [3, 24],
      },
      password: {
        minlength: 6,
      },
    },
    messages: {
      username: {
        required: "Enter your username.",
        rangelength: "Your username should consist of 3-24 characters. ",
      },
      password: {
        required: "Enter your password.",
        minlength: "Your password must be at least 6 characters.",
      },
    },
  });
};

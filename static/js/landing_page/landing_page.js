import { formValidation } from "./validationSettings.js";
const header = document.getElementById("header");
var body = document.getElementsByClassName("custom-scrollbars")[0];

body.addEventListener("scroll", () => {
  let scrollValue__Y = body.scrollTop;
  if (scrollValue__Y > 100) {
    header.classList.add("affix");
  } else {
    header.classList.remove("affix");
  }
});

// For remember me
$(function () {
  if (localStorage.chkbx && localStorage.chkbx != "") {
    $("#rememberMe").attr("checked", "checked");
    $("#username").val(localStorage.username);
    // $("#password").val(localStorage.password);
  } else {
    $("#rememberMe").removeAttr("checked");
    $("#username").val("");
    // $("#password").val("");
  }
  $("#rememberMe").click(function () {
    if ($("#rememberMe").is(":checked")) {
      // save username and passwordword
      localStorage.username = $("#username").val();
      // localStorage.password = $("#password").val();
      localStorage.chkbx = $("#rememberMe").val();
    } else {
      localStorage.username = "";
      localStorage.password = "";
      localStorage.chkbx = "";
    }
  });
  $(".submit").click(function () {
    if ($("#rememberMe").is(":checked")) {
      // save username and passwordword
      localStorage.username = $("#username").val();
      // localStorage.password = $("#password").val();
      localStorage.chkbx = $("#rememberMe").val();
    } else {
      localStorage.username = "";
      localStorage.password = "";
      localStorage.chkbx = "";
    }
  });
});

formValidation();

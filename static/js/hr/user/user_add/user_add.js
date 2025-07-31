// Select - inputs 

const id_cv_resume = document.getElementById("id_cv_resume")
const id_nondisclosure_agreement = document.getElementById("id_nondisclosure_agreement")
const id_employment_contract = document.getElementById("id_employment_contract")
const id_ssi_statement_of_employment = document.getElementById("id_ssi_statement_of_employment")

id_cv_resume.classList.add("upload");
id_nondisclosure_agreement.classList.add("upload");
id_employment_contract.classList.add("upload");
id_ssi_statement_of_employment.classList.add("upload");

var FileUpload = (function () {
    var _componentFileUpload = function () {
      if (!$().fileinput) {
        console.warn("Warning - fileinput.min.js is not loaded.");
        return;
      }
  
      //
      // Define variables
      //
  
      // Modal template
      var modalTemplate =
        '<div class="modal-dialog modal-lg" role="document">\n' +
        '  <div class="modal-content">\n' +
        '    <div class="modal-header align-items-center">\n' +
        '      <h6 class="modal-title">{heading} <small><span class="kv-zoom-title"></span></small></h6>\n' +
        '      <div class="kv-zoom-actions btn-group">{toggleheader}{fullscreen}{borderless}{close}</div>\n' +
        "    </div>\n" +
        '    <div class="modal-body">\n' +
        '      <div class="floating-buttons btn-group"></div>\n' +
        '      <div class="kv-zoom-body file-zoom-content"></div>\n' +
        "{prev} {next}\n" +
        "    </div>\n" +
        "  </div>\n" +
        "</div>\n";
  
      // Buttons inside zoom modal
      var previewZoomButtonClasses = {
        toggleheader: "btn btn-light btn-icon btn-header-toggle btn-sm",
        fullscreen: "btn btn-light btn-icon btn-sm",
        borderless: "btn btn-light btn-icon btn-sm",
        close: "btn btn-light btn-icon btn-sm",
      };
  
      // Icons inside zoom modal classes
      var previewZoomButtonIcons = {
        prev:
          $("html").attr("dir") == "rtl"
            ? '<i class="icon-arrow-right32"></i>'
            : '<i class="icon-arrow-left32"></i>',
        next:
          $("html").attr("dir") == "rtl"
            ? '<i class="icon-arrow-left32"></i>'
            : '<i class="icon-arrow-right32"></i>',
        toggleheader: '<i class="icon-menu-open"></i>',
        fullscreen: '<i class="icon-screen-full"></i>',
        borderless: '<i class="icon-alignment-unalign"></i>',
        close: '<i class="icon-cross2 font-size-base"></i>',
      };
  
      // File actions
      var fileActionSettings = {
        zoomClass: "",
        zoomIcon: '<i class="icon-zoomin3"></i>',
        dragClass: "p-2",
        dragIcon: '<i class="icon-three-bars"></i>',
        removeClass: "",
        removeErrorClass: "text-danger",
        removeIcon: '<i class="icon-bin"></i>',
        indicatorNew: '<i class="icon-file-plus text-success"></i>',
        indicatorSuccess:
          '<i class="icon-checkmark3 file-icon-large text-success"></i>',
        indicatorError: '<i class="icon-cross2 text-danger"></i>',
        indicatorLoading: '<i class="icon-spinner2 spinner text-muted"></i>',
      };
  
      //
      // Basic example
      //
  
      $(".upload").fileinput({
        browseLabel: "Browse",
        browseIcon: '<i class="icon-file-plus mr-2"></i>',
        uploadIcon: '<i class="icon-file-upload2 mr-2"></i>',
        removeIcon: '<i class="icon-cross2 font-size-base mr-2"></i>',
        layoutTemplates: {
          icon: '<i class="icon-file-check"></i>',
          modal: modalTemplate,
        },
        initialCaption: "No file selected",
        previewZoomButtonClasses: previewZoomButtonClasses,
        previewZoomButtonIcons: previewZoomButtonIcons,
        fileActionSettings: fileActionSettings,
      });
  
      // Disable/enable button
      $("#btn-modify").on("click", function () {
        $btn = $(this);
        if ($btn.text() == "Disable file input") {
          $("#file-input-methods").fileinput("disable");
          $btn.html("Enable file input");
          alert(
            "Hurray! I have disabled the input and hidden the upload button."
          );
        } else {
          $("#file-input-methods").fileinput("enable");
          $btn.html("Disable file input");
          alert(
            "Hurray! I have reverted back the input to enabled with the upload button."
          );
        }
      });
    };
  
    return {
      init: function () {
        _componentFileUpload();
      },
    };
  })();
  
  // Initialize module
  // ------------------------------
  
  document.addEventListener("DOMContentLoaded", function () {
    FileUpload.init();
  });
  
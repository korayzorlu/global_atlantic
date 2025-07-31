
// const btnToTop = document.querySelector(".btn-to-top");
const request = new Request(csrfToken);
// Loading icon

String.prototype.format = function (_key, _data) {
  return this.split(_key).map(function (value, index) { return _data[index] ? value + _data[index] : (value ? value : '') }).join("");
}

String.prototype.formatAll = function (_keys, _data) {
  let shift = () => { _keys.shift(); return _data.shift() }
  return this.split(/\s+/).map(function (value) { return value == _keys[0] ? shift() : value }).join(" ")
}

document.addEventListener("DOMContentLoaded", function () {
  //document.getElementById("load").remove();
  //menuActive();
});

(function addEventListeners() {
  window.addEventListener("scroll", windowScroll);
  // btnToTop.addEventListener("click", toTop);
})();

function toTop() {
  window.scrollTo({
    top: 0,
    left: 0,
    behavior: "smooth",
  });
}

function windowScroll() {
  let scrollValue__Y = window.scrollY;
  if (scrollValue__Y > 200) {
    //btnToTop.classList.add("btn-to-top-visible");
  } else {
    console.log(scrollValue__Y);
    //btnToTop.classList.remove("btn-to-top-visible");
  }
}

// function menuActive() {
//   //Variables
//   const titles = document.querySelectorAll(".title");
//   const pageMainTitle = document.getElementById("pageMainTitle");
//   const pageMainRoute = document.getElementById("pageMainRoute");
//   const pageChildRoute = document.getElementById("pageChildRoute");

//   titles.forEach((title) => {
//     if (pageMainTitle.innerHTML.trim().includes(title.innerHTML.trim())) {
//       let parentMenuItem = title.closest(".nav-item");
//       parentMenuItem.classList.add("nav-item-open");
//       parentMenuItem.classList.add("nav-item-expanded");

//       if (title.innerHTML.trim() !== "Dashboard") {
//         parentMenuItem.querySelector(".nav-group-sub").style.display = "block";
//         const links = parentMenuItem.querySelectorAll(".nav-link");
//         links.forEach((link) => {
//           let words = link.innerHTML.split(" ");
//           if (pageMainRoute.innerHTML.trim().includes(words[0])) {
//             let parentMainRouteItem = link.closest(".nav-item");
//             parentMainRouteItem.classList.add("nav-item-open");
//             link.nextElementSibling
//               ? link.nextElementSibling.classList.add("nav-item-open")
//               : null;
//             parentMainRouteItem.querySelector(".nav-group-sub")
//               ? (parentMainRouteItem.querySelector(
//                 ".nav-group-sub"
//               ).style.display = "block")
//               : null;
//             const childLinks = parentMenuItem.querySelectorAll(".nav-link");
//             childLinks.forEach((childLink) => {
//               var words2 = childLink.innerHTML.split(" ");
//               if (pageChildRoute.innerHTML.trim().includes(words2[0])) {
//                 let parentChildRouteItem = childLink.closest(".nav-item");
//                 parentChildRouteItem.classList.add("nav-item-open");
//               }
//             });
//           }
//         });
//       }
//     }
//   });
// }
let targetTheme = currentTheme;
const icon = document.getElementById("toggleIcon");
const iconWrapper = document.getElementById("toggleTheme");

const lightThemeVariables = function () {
  request
    .put(profile_theme_api_url, {
      theme: "light",
    })
    .then(() => {
      swalInit.fire({
        text: "Light theme loading!",
        icon: "info",
        toast: true,
        showConfirmButton: false,
        timer: 4000,
        position: "bottom-right",
        didOpen: () => {
          Swal.showLoading();
        },
      });

      icon.src = sun;
      iconWrapper.classList.add("rotate-");
      iconWrapper.classList.remove("rotate");
    })
    .then(() => {
      setTimeout(() => {
        location.reload();
      }, 100);
    });
};

const darkThemeVariables = function () {
  request
    .put(profile_theme_api_url, {
      theme: "dark",
    })
    .then(() => {
      swalInit.fire({
        text: "Dark theme loading!",
        icon: "info",
        toast: true,
        showConfirmButton: false,
        timer: 4000,
        position: "bottom-right",
        didOpen: () => {
          Swal.showLoading();
        },
      });
      icon.src = moon;
      iconWrapper.classList.add("rotate");
      iconWrapper.classList.remove("rotate-");
    })
    .then(() => {
      setTimeout(() => {
        location.reload();
      }, 100);
    });
};

$(document).on("click", "#toggleTheme", function (e) {
  if (targetTheme === "dark") {
    lightThemeVariables();
  } else {
    darkThemeVariables();
  }
});

$(function () {
  $('body').tooltip({
    selector: '[data-toggle="tooltip"]'
  });
})
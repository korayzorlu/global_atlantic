const request = new Request(_csrfToken);

const image_viewer = document.getElementById('profile-image-main');
const profile_images_css_selector = ".profile-image"
const profile_delete_button = document.getElementById('profile-remove');
var default_image = image_viewer.src;
const image_input = document.getElementsByName('image')[0];
const max_image_dimension = 512;

// probably for failed form send, can be deleted after testing
setImageToViewer(image_input, image_viewer, default_image)

image_input.addEventListener("change", function () {
    setImageToViewer(this, image_viewer, default_image)
});
profile_delete_button.addEventListener("click", removeProfileImage);

function setImageToViewer(_input, _viewer, _image) {
    if (_input.files && _input.files[0]) {
        var reader = new FileReader();
        var image_type = _input.files[0].type
        // declare an onload function
        reader.onload = function (e) {

            // compress the image data
            compress(e.target.result, image_type, max_image_dimension, 'small').then(img => {

                // crop the compressed image data as a square
                crop(img, image_type, 1).then(image => {
                    image_file = dataURLtoFile(image, _input.files[0].name);

                    // upload the final image
                    updateProfileImage(image_file).then((data) => {
                        // and add the link from API to image viewer
                        $(profile_images_css_selector).attr('src', data.image);
                        default_image = data.image;
                        // toast message
                        swalInit.fire({
                            text: "Profile image changed!",
                            icon: "success",
                            toast: true,
                            showConfirmButton: false,
                            timer: 4000,
                            position: "bottom-right",
                        });
                    })

                });
            })
        };

        // read the file
        reader.readAsDataURL(_input.files[0]);
    } else {
        _viewer.src = _image;
    }
}

// https://pqina.nl/blog/cropping-images-to-an-aspect-ratio-with-javascript/
function crop(_url, _image_type, _aspectRatio) {

    // we return a Promise that gets resolved with our canvas element
    return new Promise(resolve => {

        // this image will hold our source image data
        const inputImage = new Image();

        // we want to wait for our image to load
        inputImage.onload = () => {

            // let's store the width and height of our image
            const inputWidth = inputImage.naturalWidth;
            const inputHeight = inputImage.naturalHeight;

            // get the aspect ratio of the input image
            const inputImageAspectRatio = inputWidth / inputHeight;

            // if it's bigger than our target aspect ratio
            let outputWidth = inputWidth;
            let outputHeight = inputHeight;
            if (inputImageAspectRatio > _aspectRatio) {
                outputWidth = inputHeight * _aspectRatio;
            } else if (inputImageAspectRatio < _aspectRatio) {
                outputHeight = inputWidth / _aspectRatio;
            }

            // calculate the position to draw the image at
            const outputX = (outputWidth - inputWidth) * .5;
            const outputY = (outputHeight - inputHeight) * .5;

            // create a canvas that will present the output image
            const outputImage = document.createElement('canvas');

            // set it to the same size as the image
            outputImage.width = outputWidth;
            outputImage.height = outputHeight;

            // draw our image at position 0, 0 on the canvas
            const ctx = outputImage.getContext('2d');
            ctx.drawImage(inputImage, outputX, outputY);
            resolve(outputImage.toDataURL(_image_type));
        };

        // start loading our image
        inputImage.src = _url;
    })

}

// https://zocada.com/compress-resize-images-javascript-browser/
function compress(_url, _image_type, _limit, _related = 'big') {
    // related means: are we decreasing the size by big side or the small side
    // example for big: original image 750x1334 -> 288x512
    // example for small: original image 750x1334 -> 512x910
    return new Promise(resolve => {
        let img = new Image();

        img.onload = () => {
            let dimensions = calculateNewDimensions(img.width, img.height, _limit, _related);
            // console.log(dimensions)
            let elem = document.createElement('canvas');
            elem.width = dimensions[0];
            elem.height = dimensions[1];

            let ctx = elem.getContext('2d');
            ctx.drawImage(img, 0, 0, elem.width, elem.height);

            resolve(elem.toDataURL(_image_type, 0.85));
        }

        img.src = _url;
    })
}

// simple resolution calculation to matched given limit
function calculateNewDimensions(_width, _height, _limit, _related = 'big') {
    // if related is small, then the limit will be checked on the small side
    // else the limit will be checked on the big side
    if (_related == 'big') {
        if (_width >= _height) {
            ratio = _limit / _width;
        } else {
            ratio = _limit / _height;
        }
    } else {
        if (_width <= _height) {
            ratio = _limit / _width;
        } else {
            ratio = _limit / _height;
        }
    }

    return [Math.round(_width * ratio), Math.round(_height * ratio)];
}

// https://stackoverflow.com/a/43358515/14506165
function dataURLtoFile(_dataurl, _filename) {
    var arr = _dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], _filename, { type: mime });
}

function updateProfileImage(_image) {
    return new Promise(resolve => {
        var formData = new FormData()
        formData.append('image', _image)
        request
            .put_file(profile_image_api_url, formData)
            .then((response) => { // https://stackoverflow.com/a/38236296/14506165
                if (response.ok) {
                    $(image_input).val(''); // to accept same image
                    return response.json();
                } else {
                    response.json().then(errors => {
                        let error_text = [];
                        for (var key of Object.keys(errors)) {
                            if ($(`[name=${key}]`).length) {
                                error_text.push(`<span class="font-weight-bold">${key[0].toUpperCase() + key.slice(1)}:</span> <span>${errors[key]}</span>`);
                            } else {
                                error_text.push(`<span>${errors[key]}</span>`);
                            }
                        }
                        // modal message
                        swalInit.fire({
                            html: error_text.join("<br>"),
                            icon: "error",
                            showConfirmButton: true
                        });
                    })
                    $(image_input).val(''); // to accept same image
                    throw new Error('Something went wrong');
                }
            })
            .then((data) => { resolve(data) })
            .catch((err) => { console.log(err) });
    })
};

function removeProfileImage() {
    sweetCombine(
        "Are you sure?",
        "You won't be able to revert this!",
        "warning",
        "delete",
        () => {
            let formData = new FormData()
            formData.append('image', '')
            request
                .put_file(profile_image_api_url, formData)
                .then((response) => { // https://stackoverflow.com/a/38236296/14506165
                    if (response.ok) {
                        $(profile_images_css_selector).attr('src', $(image_viewer).data("default"));
                        $(image_input).val(''); // to accept same image
                    } else {
                        response.json().then(errors => {
                            let error_text = [];
                            for (var key of Object.keys(errors)) {
                                if ($(`[name=${key}]`).length) {
                                    let name = key.replace('_', ' ')
                                    error_text.push(`<span class="font-weight-bold text-capitalize">${name}:</span> <span>${errors[key]}</span>`);
                                } else {
                                    error_text.push(`<span>${errors[key]}</span>`);
                                }
                            }
                            // modal message
                            swalInit.fire({
                                html: error_text.join("<br>"),
                                icon: "error",
                                showConfirmButton: true
                            });
                        })
                        $(image_input).val(''); // to accept same image
                        throw new Error('Something went wrong');
                    }
                })
        },
        "Deleted!",
        "Profile image has been deleted.",
        "success",
        () => console.error("error --> Profile image delete canceled."),
        "Cancelled!",
        "Your profile image is safe :)",
        "error"
    );
}
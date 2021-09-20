let formData = new FormData();

$(document).ready(function () {

    Array.prototype.forEach.call(document.querySelectorAll(".file-upload__button2"),
        function (button) {
            button.addEventListener("click", function () {
                uploadFile(formData);
                console.log(formData.getAll("path"));
                [...formData.entries()].forEach((row) => {
                    console.log(row);
                });

            });
        });

    Array.prototype.forEach.call(
        document.querySelectorAll(".file-upload__button"),
        function (button) {

            const hiddenInput = button.parentElement.querySelector(
                ".file-upload__input"
            );
            const label = button.parentElement.querySelector(".file-upload__label");
            const defaultLabelText = "No file(s) selected";

            // Set default text for label
            label.textContent = defaultLabelText;
            label.title = defaultLabelText;

            button.addEventListener("click", function () {
                hiddenInput.click();
                console.log("clicked1");
            });

            hiddenInput.addEventListener("change", function () {
                let files = $(this)[0].files;

                // Loop through files
                for (let i = 0; i < files.length; i++) {
                    formData.append("path", files[i])
                }


                // files.forEach(function (e) {
                //     console.log(e);
                // });
                //
                //
                // ($(this)[0].files).forEach(function (file) {
                //     console.log(file.name)
                //     formData.append("path", file)
                // });

                const filenameList = Array.prototype.map.call(hiddenInput.files, function (
                    file
                ) {
                    return file.name;
                });

                label.textContent = filenameList.join(", ") || defaultLabelText;
                label.title = label.textContent;
            });
        }
    );

});


function uploadFile(formData) {
    var url = 'http://127.0.0.1:5000/api/v1/resources/files/path'

    // evt.preventDefault();
    // var formData = new FormData($(this)[0]);
    $.ajax({
        url: url,
        type: 'POST',
        data: formData,
        async: false,
        cache: false,
        contentType: false,
        enctype: 'multipart/form-data',
        processData: false,
        success: function (response) {
            alert(response);
        }
    });
}
$(document).ready(function () {

    Array.prototype.forEach.call(document.querySelectorAll(".file-download-report__button"),
        function (button) {
            button.addEventListener("click", function () {
                dateFrom = document.getElementById("dateFrom").value
                dateTo = document.getElementById("dateTo").value
                console.log("clicked download report");
                console.log("clicked download report" + dateFrom);
                console.log("clicked download report" + dateTo);
                if (dateFrom && dateTo) {
                    downloadReport(dateFrom, dateTo);
                } else {
                    alert("Please Choose Start and End Date");
                }


            });
        });
});
// function openForm() {
//   document.getElementById("form-popup").style.display = "block";
// }
//
// function closeForm() {
//   document.getElementById("form-popup").style.display = "none";
// }
function downloadReport(from, to) { //todo when download add to db too
    var url = 'http://127.0.0.1:5000/api/v1/resources/database/show?dateFrom=' + from + '&dateTo=' + to;

    // evt.preventDefault();
    $.ajax({
        url: url,
        type: 'GET',
        data: [from, to],

        success: function (response) {
            alert(response);
        }
    });
}
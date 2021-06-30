// $(document).ready(function () {
//     console.log("on ready")
//     $.ajax({
//         type: "POST",
//         url: "http://127.0.0.1:5000/liveStream",
//         headers: {
//             'Access-Control-Allow-Origin': '*'
//         },
//         success: function (data) {
//             console.log("success: "+ data)
//             document.getElementById("socketIMG").setAttribute('src', data)
//         },
//         error: function (error) {
//             console.error(error)
//         }
//     });
// })

window.addEventListener("beforeunload", function (e) {
    // var confirmationMessage = "\o/";
    e.preventDefault()
    console.log("onbeforeunload")
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/stopStream",
        headers: {
            'Access-Control-Allow-Origin': '*'
        },
        success: function (data) {
            console.log("success: " + data)
        },
        error: function (error) {
            console.error(error)
        }
    });
});
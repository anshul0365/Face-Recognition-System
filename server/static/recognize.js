window.addEventListener("beforeunload", function (e) {
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
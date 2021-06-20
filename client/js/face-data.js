// window.onload = function () {
//     Particles.init({
//         selector: '.background-particle',
//         color: '#cacaca',
//         connectParticles: true,
//         speed: 0.2,
//         maxParticles: 150,
//         sizeVariations: 3,
//         minDistance: 100
//     });
// };
const video = document.querySelector("#liveStream");
const canvas = document.querySelector('#liveStreamCanvas');
let timeCount = 1;

function startVideoStream() {
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
                startCapturing()
            })
            .catch(function (error) {
                console.log("Something went wrong!");
            });
    }
}

function startCapturing() {
    let timer = setInterval(function () {
        captureImage();
        console.log(timeCount);

        if (timeCount > 2) {
            clearInterval(timer);
            console.log("Closing Video Stream");
            stopVideoStream();
            // return
        }
        timeCount++;
    }, 1000); //time in millisecond
}

function captureImage() {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
    let data = canvas.toDataURL('image/png');
    canvas.setAttribute('src', data);
    // img.src = canvas.toDataURL();
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/saveImage",
        headers: {
            // 'Access-Control-Allow-Origin': '*'
        },
        data: {
            imageData: data
        },
        success: function (data) {
            console.log(data);
        },
        error: function (error) {
            console.error(error)
        }
    });
}

function stopVideoStream() {
    const nextBtn = document.getElementById('step-1-next-btn');
    nextBtn.removeAttribute('disabled');
    
    try {
        video.srcObject.getTracks().forEach((track) => {
            track.stop();
        })
        console.log("Video Stream closed")
        // video.setAttribute('poster', canvas.toDataURL('image/png')) ;
    } catch (error) {
        console.error("Unable to stop video stream\n" + error);
    }
}

function getName(faceLabel) {
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/getName",
        headers: {
            // 'Access-Control-Allow-Origin': '*'
        },
        data: {
            name: faceLabel
        },
        success: function (data) {
            console.log(data);
            verify(data)
        },
        error: function (jqXHR) {
            console.log(jqXHR);
            verify(jqXHR)
        }
    });
}

function verify(data) {
    let redirectCount = 10;
    if (data.status == 200 || data.statusText=="success") {
        document.getElementById('step-2').style.display = "none";
        document.getElementById('step-3').style.display = "flex";
    }
    else {
        document.getElementById('step-2').style.display = "none";
        document.getElementById('step-3-error').style.display = "flex";
    }

    let redirectTimer = setInterval(function () {
        console.log(redirectCount);
        
        const redirectCountEle = document.getElementById('redirectCount');
        const redirectCountEleErr = document.getElementById('redirectCount-error');
        
        redirectCountEle.innerText = redirectCount;
        redirectCountEleErr.innerText = redirectCount;

        if (redirectCount <= 0) {
            clearInterval(redirectTimer);
            console.log("Redirecting to homepage");
            window.location.href = "../index.html";
        }
        redirectCount--;
    }, 1000); //time in millisecond
}


$(document).ready(function () {
    $('#tipsModal').modal('show');
});

$('#btn-tips-modal').click(function () {
    console.log("Tips Modal clicked");
    startVideoStream();
});

$('#step-1-next-btn').click(function () {
    console.log("next btn clicked");
    document.getElementById('step-1').style.display = "none";
    document.getElementById('step-2').style.display = "flex";
});

$('#step-2-submit-btn').click(function (e) {
    e.preventDefault();
    console.log("submit btn clicked");
    const faceLabel = document.getElementById('faceLabel').value;
    getName(faceLabel)
});
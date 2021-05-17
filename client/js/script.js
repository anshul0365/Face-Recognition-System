$(document).ready(function () {
    var video = document.getElementsByTagName('video')[0];
    video.height = window.innerHeight
    console.log(video.height)
});

$(window).resize(function () {
    var video = document.getElementsByTagName('video')[0];
    video.height = window.innerHeight
    console.log(video.height)
});
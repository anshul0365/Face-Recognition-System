window.onload = function () {
    Particles.init({
        selector: '.background-particle',
        color: '#cacaca',
        connectParticles: true,
        speed: 0.2,
        maxParticles: 150,
        sizeVariations: 3,
        minDistance: 100
    });
};
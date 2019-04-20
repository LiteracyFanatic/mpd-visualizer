let canvas;
let ctx;
let socket = new WebSocket("ws://localhost:8765");
let dpi = window.devicePixelRatio;

const scaling = 10;


function fix_dpi() {
    //get CSS height
    //the + prefix casts it to an integer
    //the slice method gets rid of "px"
    let style_height = +getComputedStyle(canvas).getPropertyValue("height").slice(0, -2);
    //get CSS width
    let style_width = +getComputedStyle(canvas).getPropertyValue("width").slice(0, -2);
    //scale the canvas
    canvas.setAttribute('height', style_height * dpi);
    canvas.setAttribute('width', style_width * dpi);
}

window.addEventListener("load", event => {

    socket.addEventListener('message', function (event) {
        magnitudes = JSON.parse(event.data);
        draw(magnitudes);
    });

    canvas = document.getElementById("frequency-spectrum-canvas");
    fix_dpi();

    ctx = canvas.getContext("2d");
    ctx.setTransform(1, 0, 0, -1, 0, canvas.height);
});

function draw(magnitudes) {
    const t_0 = performance.now();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width / magnitudes.length;
    const gap = w / 8;
    const gradientHeight = canvas.height / 6;
    ctx.beginPath();
    ctx.moveTo(0, gradientHeight);
    ctx.lineTo(canvas.width, gradientHeight);
    ctx.stroke();
    const gradient = ctx.createLinearGradient(canvas.width / 2, 0, canvas.width / 2, gradientHeight);
    gradient.addColorStop(0, "#3366b2");
    gradient.addColorStop(1, "#91faff");
    ctx.fillStyle = gradient;
    for (let i = 0; i < magnitudes.length; i++) {
        ctx.fillRect(i * w + gap, 0, w - 2 * gap, scaling * magnitudes[i]);
    }
    const t_1 = performance.now();
    const dt = t_1 - t_0;
    console.log(dt);
}

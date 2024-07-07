let box = document.querySelector('#content-box');
let pen = document.querySelector('img.pen');
let nb_clicks = 0;
let follows = false;
let activate = false;
var rect, contentCoords;
let coordX = 0;
let coordY = 0;

let origin_rect = (x, y) => `
    position: absolute;
    top: ${y}px;
    left: ${x}px;
    border: 2px red dashed;
`

pen.addEventListener('click', () => {
    if (activate){
        activate = false;
        pen.classList.remove('active-icon');
    } else{
        activate = true;
        pen.classList.add('active-icon');
    }
});

box.addEventListener('mousemove', (e) => {
    contentCoords = box.getBoundingClientRect();
    coordX = e.pageX - contentCoords.left - window.scrollX;
    coordY = e.pageY - contentCoords.top - window.scrollY;
})

box.addEventListener('mousedown', (e) => {
    if (!activate)
        return;
    nb_clicks++;
    if (nb_clicks % 2 != 0){
        // let x = e.clientX, y = e.clientY;
        follows = true;
        rect = document.createElement('div');
        rect.style.cssText = origin_rect(coordX, coordY);
        box.appendChild(rect);
    } else {    // When the second click append, the rect is handled one last time
        const currentRectCoords = rect.getBoundingClientRect();
        contentCoords           = box.getBoundingClientRect();
        const x0 = parseInt(currentRectCoords.left - contentCoords.left);
        const x1 = parseInt(currentRectCoords.left - contentCoords.left + currentRectCoords.width);
        const y0 = parseInt(currentRectCoords.top - contentCoords.top);
        const y1 = parseInt(currentRectCoords.top - contentCoords.top + currentRectCoords.height);
        rect.setAttribute('bbox', `[${x0}, ${y0}, ${x1}, ${y1}]`);
        rect.setAttribute('page', currPage);
        follows = false;
    }
})

function drawRectangle(){
    if (!activate || !follows)
        return;
    contentCoords = box.getBoundingClientRect();
    x = contentCoords.width - coordX; 
    y = contentCoords.height - coordY;
    // console.log(rect);
    rect.style.right = x + 'px';
    rect.style.bottom = y + 'px';

}



setInterval(drawRectangle, 100)
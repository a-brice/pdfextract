let box = document.querySelector('#content-box');
let pen = document.querySelector('img.pen');
let can = document.querySelector('img.can');
let boxnameInput = document.querySelector('#box-name');
let nb_clicks = 0;
let nb_rects = 0;
let follows = false;
let activateDrawing = false;
let activateDrop = false;
var rect, contentCoords;
let originPoint = [];
let coordX = 0;
let coordY = 0;
let typeBtn = ['#r-text', '#r-dig', '#r-box'];


pen.addEventListener('click', () => {
    activateDrop = false;
    can.classList.remove('active-icon');

    if (activateDrawing){
        activateDrawing = false;
        pen.classList.remove('active-icon');
        box.classList.remove('ch-cursor');
    } else{
        activateDrawing = true;
        pen.classList.add('active-icon');
        box.classList.add('ch-cursor');
    }        
});

can.addEventListener('click', () => {
    activateDrawing = false;
    pen.classList.remove('active-icon');
    box.classList.remove('ch-cursor');

    if (activateDrop){
        activateDrop = false;
        can.classList.remove('active-icon');
    } else{
        activateDrop = true;
        can.classList.add('active-icon');
    }        
});

box.addEventListener('mousemove', (e) => {
    contentCoords = box.getBoundingClientRect();
    coordX = e.pageX - contentCoords.left - window.scrollX;
    coordY = e.pageY - contentCoords.top - window.scrollY;
})

box.addEventListener('mousedown', (e) => {
    if (!activateDrawing || e.which == 3)
        return;
    nb_clicks++;
    if (nb_clicks % 2 != 0){
        // let x = e.clientX, y = e.clientY;
        let type = document.querySelector('input[name="type"]:checked').value;
        follows = true;
        nb_rects++;
        rect = document.createElement('div');
        rect.classList.add('rect-box');
        rect.innerHTML = `<span class="label-span" ${showLabelRect ? '': 'style="display: none"'}>${nb_rects}; ${type}</span>`
        rect.style.cssText = setOriginRect(coordX, coordY);
        box.appendChild(rect);
        rect.setAttribute('label', nb_rects);
        boxnameInput.value = nb_rects;

    } else {    // When the second click append, the rect is handled one last time
        setRectBbox();
        setRectType();
        clickOnRect(rect);
        follows = false;
    }
})

typeBtn.forEach(btn => {
    document.querySelector(btn).addEventListener('click', setRectType);
})


function clickOnRect(Rect){
    Rect.onclick = (e) => { 
        if (activateDrop) 
            e.target.remove();  
        if (!activateDrawing && !activateDrop){
            rect = e.target;
            boxnameInput.value = rect.getAttribute('label');
            if (rect.getAttribute('type') == 'Box'){
                document.querySelector('input#r-box').checked = true;
            } else if (rect.getAttribute('type') == 'Digit') {
                document.querySelector('input#r-dig').checked = true;
            } else {
                document.querySelector('input#r-text').checked = true;
            }
        }              
    } 

}


function setRectBbox(){
    const currentRectCoords = rect.getBoundingClientRect();
    contentCoords           = box.getBoundingClientRect();
    const x0 = Math.round(currentRectCoords.left - contentCoords.left);
    const x1 = Math.round(currentRectCoords.left - contentCoords.left + currentRectCoords.width);
    const y0 = Math.round(currentRectCoords.top - contentCoords.top);
    const y1 = Math.round(currentRectCoords.top - contentCoords.top + currentRectCoords.height);
    rect.setAttribute('bbox', `[${x0}, ${y0}, ${x1}, ${y1}]`);
    rect.setAttribute('page', currPage);
}

function setOriginRect(x, y){
    originPoint = [x, y];
    return `
        position: absolute;
        top: ${y}px;
        left: ${x}px;
        border: 2px red dashed;
    `
}

function setRectType(){
    let type = document.querySelector('input[name="type"]:checked').value;
    rect.setAttribute('type', type);
    rect.querySelector('.label-span').textContent = rect.getAttribute('label') + ';' + type;
}


function drawRectangle(){
    if (!activateDrawing || !follows)
        return;
    contentCoords = box.getBoundingClientRect();
    let [x0, y0] = originPoint;
    let [x, y] = [coordX, coordY];
    rect.style.width = Math.abs(x - x0) + 'px';
    rect.style.height = Math.abs(y - y0) + 'px';

    if (x < x0) rect.style.left = x + 'px';
    else rect.style.left = x0 + 'px';
    
    if (y < y0) rect.style.top = y + 'px';
    else rect.style.top = y0 + 'px';
}

boxnameInput.addEventListener('input', (e) => {
    if (rect !== undefined){
        rect.setAttribute('label', e.target.value);
        rect.querySelector('.label-span').textContent = e.target.value + ';' + rect.getAttribute('type');
    }
})



setInterval(drawRectangle, 100)

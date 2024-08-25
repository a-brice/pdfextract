// variable : box, contentCoords, nb_rects, clickOnRect() => draw.js
// currPage : html template (drawing.html)

let inputFile = document.getElementById('json');

function putRects(obj){
    
    for (let i = 0; i < obj.length; i++){
        let contentCoords = box.getBoundingClientRect();
        let newrect = document.createElement('div');
        newrect.classList.add('rect-box');
        newrect.innerHTML = `<span class="label-span" ${!showLabelRect ? 'style="display: none"' : ''}>${obj[i].label}, ${obj[i].type}</span>`
        newrect.style.cssText = `
            position: absolute;
            left: ${obj[i].bbox[0]}px;
            top: ${obj[i].bbox[1]}px;
            width: ${Math.abs(obj[i].bbox[0] - obj[i].bbox[2])}px;
            height: ${Math.abs(obj[i].bbox[1] - obj[i].bbox[3])}px;
            border: 2px darkred dashed;
            ${currPage != obj[i].page ? "display: none": ""}
        `
        newrect.setAttribute('label', obj[i].label);
        newrect.setAttribute('page', obj[i].page);
        newrect.setAttribute('type', obj[i].type);
        newrect.setAttribute('bbox', JSON.stringify(obj[i].bbox));
        nb_rects++;
        clickOnRect(newrect);
        box.appendChild(newrect);
    }
}


inputFile.addEventListener('input', e => {
    inputFile.files[0].text().then(
        res => JSON.parse(res)
    ).then(
        obj => putRects(obj['drawing'])
    );    
})
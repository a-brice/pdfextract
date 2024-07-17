
let dload = document.querySelector('.icon.download');
let req; 

function getDrawing(){
    let rectPos = [];
    let rects = document.querySelectorAll('.rect-box');
    rects.forEach((e) => {
        let attrs = {
            label:e.getAttribute('label'),
            bbox:e.getAttribute('bbox'),
            page:e.getAttribute('page'),
            type:e.getAttribute('type')
        }
        rectPos.push(attrs);
    })
    return (rectPos)
}


dload.onclick = () => {
    let drawing = getDrawing();

    req = fetch(urlSave, {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify(drawing)
    }).then(res => {
        if (res.ok){            
            location.href = urlDload;
        }
        else{
            alert("Drawings could not be uploaded ! ");
        }
    });
}
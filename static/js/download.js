
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
    let _1toN = document.querySelector('#_1toN').checked;
    let pageN = parseInt(document.querySelector('#pageN').value) - 1;
    let config = {
        dpi: dpi,
        _1toN: _1toN,
        _1toNonPage: pageN,
        drawing: drawing
    }

    req = fetch(urlSave, {
        method: 'POST',
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify(config)
    }).then(res => {
        if (res.ok){            
            location.href = urlDload;
        }
        else{
            alert("Config could not be uploaded ! ");
        }
    });
}
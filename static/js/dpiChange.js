let dpiBtn = document.querySelector('.set-dpi');
let newDpi; 

dpiBtn.addEventListener('click', () => {
    newDpi = parseInt(document.querySelector('input[name="dpi"]').value);
    let formData = new FormData();
    formData.append('dpi', newDpi);
    formData.append('sess_id', sess_id);
    fetch('/draw/', {
        method: 'PUT', 
        body: formData
    }).then(
        res => { 
            if (!res.ok)
                console.log('Something wrong appened !');
            goFirstPage();
            adaptDrawing(newDpi);
         }
    )
})


function applyDPI(arr, olddpi, newdpi){
    return arr.map(x => Math.round(x / olddpi * newdpi));
}

function adaptDrawing(newDpi){
    let drawing = getDrawing();
    let newDrawing = [];
    drawing.map(x => {
        newDrawing.push(
            {
                label: x.label,
                bbox: applyDPI(JSON.parse(x.bbox), dpi, newDpi),
                page: x.page,
                type: x.type
            }
        )
    })
    document.querySelectorAll('.rect-box').forEach(x => x.remove());
    putRects(newDrawing);
    dpi = newDpi;
}
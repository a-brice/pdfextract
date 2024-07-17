let iptFile = document.querySelector('#pdf-file');
let labelfile = document.querySelector('.lbl-file');

iptFile.addEventListener('dragenter', () => {
    iptFile.style.borderStyle = 'dashed';
    labelfile.textContent = "Drop here";
});

iptFile.addEventListener('dragleave', () => {
    if (iptFile.files.length == 0){
    iptFile.style.borderStyle = 'dashed';
        labelfile.textContent = "Please load or drop the PDF files you want extract data from";
    } else{
        let label = iptFile.files[0].name;
        for (let i = 1; i < iptFile.files.length; i++){
            label += ', ', iptFile.files[i].name;
        }
        labelfile.textContent = "Files dropped : \n" + label;
        document.querySelector('.icon-doc').classList.remove('hiding');
        iptFile.style.borderStyle = 'solid';
    }
})

iptFile.addEventListener('input', () => {
    dzone.style.display = 'none';

    let label = iptFile.files[0].name;
    for (let i = 1; i < iptFile.files.length; i++){
        label += ', ', iptFile.files[i].name;
    }
    labelfile.textContent = "Files dropped : \n" + label;
    document.querySelector('.icon-doc').classList.remove('hiding');
    iptFile.style.borderStyle = 'solid';
})
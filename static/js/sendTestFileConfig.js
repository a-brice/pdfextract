let form = document.querySelector('form.drop');
let dzone = document.querySelector('.btn-dload-div');
let submitBtn = document.querySelector('.next-btn');
let csvBtn = document.querySelector('.dload-csv');
let jsonBtn = document.querySelector('.dload-json');
let loading = document.querySelector('.loading');
let onSubmission = false;
let _sess_id; 

submitBtn.addEventListener('click', e => {
    e.preventDefault();
    if (onSubmission)
        return;
    
    onSubmission = true;
    loading.style.display = 'block';

    fetch(form.action, {
        method: 'POST',
        body: new FormData(form)
    }).then(
        res => {
            onSubmission = false;
            loading.style.display = 'none';
            if (res.ok){
                dzone.style.display = 'flex';
            } else {
                alert('Something wrong append !');
            }
            return res.json();
        }
    ).then(data => {
        sess_id = data['sess_id'];
        csvBtn.href = urlCSVDload + `?sess_id=${sess_id}`;
        jsonBtn.href = urlJSONDload + `?sess_id=${sess_id}`;
    });
})


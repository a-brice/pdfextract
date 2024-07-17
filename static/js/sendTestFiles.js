let form = document.querySelector('.drop');
let dzone = document.querySelector('.btn-dload-div');
let submitBtn = document.querySelector('.next-btn');
let loading = document.querySelector('.loading');
let onSubmission = false;

submitBtn.addEventListener('click', e => {
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
                dzone.style.display = 'block';
            } else {
                alert('Something wrong append !');
            }
        }
    )
})


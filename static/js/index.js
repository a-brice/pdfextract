let form = document.querySelector('form');
form.querySelector('input#tpt').onchange = (e) => {
    form.submit();
}
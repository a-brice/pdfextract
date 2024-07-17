let eyesIcon = document.querySelectorAll('.eye');
let showLabelRect = false;
let showEye = () => {
    eyesIcon.forEach(e => e.classList.toggle('hide'));
    showLabelRect = showLabelRect ? false: true;
    document.querySelectorAll('.label-span').forEach(span => {
        if (!showLabelRect)
            span.style.display = 'none';
        else
            span.style.display = 'block';
    })
};
eyesIcon[0].addEventListener('click', showEye);
eyesIcon[1].addEventListener('click', showEye);
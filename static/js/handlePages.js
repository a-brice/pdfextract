
function pageChange(page){
    // Get the new src of image
    pdf.src = `/media/${sess_id}/${page}?t=${new Date().getTime()}`;

    console.log(page);
    // Change the visibility of box that aren't in the current page
    let rects = document.querySelectorAll('.rect-box');
    rects.forEach((e) => {
        if (page !== parseInt(e.getAttribute('page')))
            e.style.display = 'none';
        else
            e.style.display = 'block';
    })
}

function goFirstPage(){
    noPageInput.value = 1;
    pageChange(0);
}


rightArrow.onclick = () => {
    if (maxPage > currPage + 1){
        currPage++;
        noPageInput.value = currPage+1;
        pageChange(currPage);
    }
}

leftArrow.onclick = () => {
    if (currPage - 1 >= 0){
        currPage--;
        noPageInput.value = currPage+1;
        pageChange(currPage);
    }
}

noPageInput.onkeydown = (e) => {
    if (e.key !== 'Enter')
        return;
    let newpage = parseInt(noPageInput.value)
    if (currPage != newpage &&  newpage > 0 && newpage <= maxPage){
        currPage = newpage - 1;
        pageChange(currPage);
    }
}
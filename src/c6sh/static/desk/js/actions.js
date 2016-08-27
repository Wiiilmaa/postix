function openDrawer() {
    console.log('calling in')
    $.ajax({
        url: '/api/cashdesk/open-drawer/',
        method: 'POST',
    })
}

function reprintReceipt() {

}

function init_actions() {
    // Initializations at page load time
    $("#btn-open-drawer").mousedown(openDrawer);
    $("#btn-reprint").mousedown(reprintReceipt);
}

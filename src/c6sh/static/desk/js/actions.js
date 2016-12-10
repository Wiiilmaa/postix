function openDrawer() {
    $.ajax({
        url: '/api/cashdesk/open-drawer/',
        method: 'POST',
    })
}

function reprintReceipt() {
    $.ajax({
        url: '/api/cashdesk/reprint-receipt/',
        method: 'POST',
        dataType: 'json',
        data: JSON.stringify({
            transaction: transaction.last_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        },
    })
}

function displayNext() {
    $.ajax({
       url: '/api/cashdesk/display-next/',
       method: 'POST',
   })
}

function requestResupply() {
    $.ajax({
        url: '/api/cashdesk/request-resupply/',
        method: 'POST',
    })
}

function init_actions() {
    // Initializations at page load time
    $("#btn-open-drawer").mousedown(openDrawer);
    $("#btn-reprint").mousedown(reprintReceipt);
    $("#btn-resupply").mousedown(requestResupply);
}

$('#active-sessions-table tr').hover(function() {
    const pk = $(this).data("session");
    if (pk) {
	$(`[data-session="${pk}"]`).addClass("coactive");
    }
}, function() {
    const pk = $(this).data("session");
    if (pk) {
	$(`[data-session="${pk}"]`).removeClass("coactive");
    }
})

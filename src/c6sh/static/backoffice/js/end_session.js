var table_body = $('#session-items_table tbody');

var get_difference = function(numberinput) {
	var row = $(numberinput).closest("tr");
    var after = parseFloat($(numberinput).val()) || 0;
    var before = parseFloat(row.find(".before-value").text());
	var transaction = parseFloat(row.find(".transaction-value").text());
    var end = parseFloat(row.find(".end-column").text()) || 0;

    if (row[0].id == 'cash') {
	    var difference = (before + transaction) - end - after;
    } else {
	    var difference = (before - transaction) - end - after;
    }

	result_cell = row.find(".after-value");
	result_cell.html(difference);
	if (difference != 0) {
		result_cell.addClass("danger");
		result_cell.removeClass("success");
    } else {
		result_cell.removeClass("danger");
		result_cell.addClass("success");
    }
}

$('.numberinput').on('keyup', function() {
    get_difference($(this));
});
$('.numberinput').each(function(index) {
    get_difference($(this));
});
$('.show-hide-heading').on('click', function() {
    $(this).nextAll('.show-hide-div').toggle();
});

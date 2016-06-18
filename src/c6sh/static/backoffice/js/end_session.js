var table_body = $('#session-items_table tbody');

var get_difference = function() {
	var row = $(this).closest("tr");
    var after = parseFloat($(this).val());
    var before = parseFloat(row.find(".before-value").text());
	var transaction = parseFloat(row.find(".transaction-value").text());
	var difference = (before - transaction) - after;

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

$('.numberinput').each(function(index) {
    console.log(this);
    $(this).on('keyup', get_difference);
})
$('.show-hide-heading').on('click', function() {
    $(this).nextAll('.show-hide-div').toggle();
});

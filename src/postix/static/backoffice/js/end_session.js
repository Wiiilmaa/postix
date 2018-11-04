var table_body = $('#session-items_table tbody');

var get_difference = function(numberinput) {
	var row = $(numberinput).closest("tr");
    var after = parseFloat($(numberinput).val().replace(",", ".")) || 0;
    var before = parseFloat(row.find(".before-value").text().replace(",", "."));
	var transaction = parseFloat(row.find(".transaction-value").text().replace(",", "."));
    var end = parseFloat(row.find(".end-column").text().replace(",", ".")) || 0;
    var difference;

    if (row[0].id === 'cash') {
        difference = before + transaction - after;
        difference = difference.toFixed(2);
    } else {
        difference = before - transaction - after;
        difference = difference.toFixed(0);
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

$('.numberinput, .calculatorwidget').on('keyup', function() {
    get_difference($(this));
});
$('.numberinput, .calculatorwidget').each(function(index) {
    get_difference($(this));
});
$('.show-hide-heading').on('click', function() {
    $(this).nextAll('.show-hide-div').toggle();
});

var backoffice_users = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: backoffice_users
});

$('#id_session-backoffice_user').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
},
{
    name: 'backoffice_users',
    source: backoffice_users

});

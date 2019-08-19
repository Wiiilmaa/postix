var table_body = $('#session-items_table tbody');

var removeSelected = function () {
  var selected = [];
  table_body.find("select").each(function () {
    selected.push($(this).val());
  });
  table_body.find("option:not([value=''])").each(function () {
    var $opt = $(this);
    $(this).prop("disabled", selected.indexOf($opt.val()) > -1 && $opt.val() !== $(this).closest("select").val());
  });
};

var addAnotherLine = function() {
    var form_count = table_body.children().length;
    if (form_count === $(table_body.find('select').first().find('option')).length) {
      return;
    }
    var item_form = $('#item-template').html().replace(/__prefix__/g, form_count);
    $(table_body.find('> :last-child select')).off('change', addAnotherLine);
    table_body.append(item_form);
    $('#id_items-TOTAL_FORMS').val(form_count+1);
    $(table_body.find('> :last-child select')).change(addAnotherLine);
    $(table_body.find('> :last-child select')).change(removeSelected);
};

$(table_body.find('> :last-child select')).change(addAnotherLine);
$(table_body.find('> :last-child select')).change(removeSelected);
$('#add_more').click(addAnotherLine);

var users = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: users
});

$('#id_session-user').typeahead({
    hint: true,
    highlight: true,
    minLength: 1

},
{
    name: 'users',
    source: users

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
$('#id_backoffice_user').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
},
{
    name: 'backoffice_users',
    source: backoffice_users

});

if (carriers) {
    var carriers = new Bloodhound({
	datumTokenizer: Bloodhound.tokenizers.whitespace,
	queryTokenizer: Bloodhound.tokenizers.whitespace,
	local: carriers
    });


    $('#id_carrier').typeahead({
	hint: true,
	highlight: true,
	minLength: 1
    },
    {
	name: 'carrier',
	source: carriers

    });
}

if ($("#id_data-cashdesk").find(":selected").text() == "---------") {
    $("#id_data-cashdesk").focus();
} else {
    $("#id_data-user").focus();
}

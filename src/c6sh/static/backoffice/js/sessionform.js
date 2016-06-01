var table_body = $('#session-items_table tbody');

var addAnotherLine = function() {
    var form_count = table_body.children().length;
    var item_form = $('#item-template').html().replace(/__prefix__/g, form_count);
    $(table_body.find('> :last-child select')).off('change');
    table_body.append(item_form)
    $('#id_items-TOTAL_FORMS').val(form_count+1);
    $(table_body.find('> :last-child select')).change(addAnotherLine);
};

$(table_body.find('> :last-child select')).change(addAnotherLine);
$('#add_more').click(addAnotherLine);

var users = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: user_list
});

$('#id_data-user').typeahead({
    hint: true,
    highlight: true,
    minLength: 1

},
{
    name: 'users',
    source: users

});

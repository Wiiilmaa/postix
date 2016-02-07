$(function () {
    $('#btn-checkout').mousedown(function() {
        $('#lower-right').addClass('post-sale');
    });
    $('#btn-clear').mousedown(function() {
        $('#lower-right').removeClass('post-sale');
    });
    $('.product button').mousedown(function() {
        $('body').addClass('has-modal');
    });
    $('#btn-cancel').mousedown(function() {
        $('body').removeClass('has-modal');
    });
    var preSaleTickets = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      limit: 4,
      remote: {
        url: '/api/preorderpositions/?search=%QUERY',
        wildcard: '%QUERY',
        transform: function(object) {
            results = object.results;
            secrets = [];
            for(var preorder in results){
                secrets.push(
                    {   
                        value: results[preorder].secret,
                        count: 1 
                    });
            }
            return secrets;
        }
      }
    });

    $('#preorder-input').typeahead(null, {
      name: 'preSaleTickets',
      display: 'value',
      minLength: 5,
      source: preSaleTickets
    });
});
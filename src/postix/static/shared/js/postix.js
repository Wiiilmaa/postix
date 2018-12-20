$('.collapse').collapse()

$('.nav-fold a[data-toggle=nav]').click(function (e) {
    $(this).parent().parent().find('div').stop().slideToggle();
    e.preventDefault();
    return false;
})

$(document).ready(function () {
    $("body").on( "swiperight", function( event ) {
        if(event.swipestart.coords[0] < $('body').width() * .1) {
            $('.row-offcanvas').addClass('active')
        }
    });

    $("body").on( "swipeleft", function( event ) {
        $('.row-offcanvas').removeClass('active')
    });

    $('[data-toggle="offcanvas"]').click(function () {
        $('.row-offcanvas').toggleClass('active')
    });
});

$(document).ready(function () {
    $("body").on( "swiperight", function( event ) {
        if(event.swipestart.coords[0] < $('body').width() * .1) {
            $('.nav-menu').offcanvas('show');
        }
    });

    $("body").on( "swipeleft", function( event ) {
        $('.nav-menu').offcanvas('hide');
        $('body').off('touchmove.bs');
    });
});

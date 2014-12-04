$(document).ready(function () {
    $("body").on( "swiperight", function( event ) {
        if(event.swipestart.coords[0] < $('body').width() * .1) {
            $('.nav-menu:not(.offcanvas-clone):not(:visible)').offcanvas('show');
        }
    });

    $("body").on( "swipeleft", function( event ) {
        $('.nav-menu.in:not(.offcanvas-clone)').offcanvas('hide');
    });

    $(".offcanvas-xs").on("show.bs.offcanvas", function(event) {
        $(".navbar-toggle").addClass("active");
    });

    $(".offcanvas-xs").on("hidden.bs.offcanvas", function(event) {
        $(".navbar-toggle").removeClass("active");
    });
});

// fixes anchor links being offset by fixed header
$(document).ready(function() {
    if (window.location.hash) {
        var hash = window.location.hash;
        $('html, body').animate({
            scrollTop: $(hash).offset().top - $('.navbar').outerHeight(true)
        }, 2000);
    }
});

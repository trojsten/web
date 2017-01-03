// fixes anchor links being offset by fixed header
$(document).ready(function() {
    if (window.location.hash) {
        var hash = window.location.hash;
        $('html, body').animate({
            scrollTop: $(hash).offset().top - 65
        }, 2000);
    }
});
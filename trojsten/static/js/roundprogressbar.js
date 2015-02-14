function refresh_progressbar(element) {
    id = $(element).data('id');
    if (typeof id !== 'undefined') {
        url = "/ulohy/ajax/" + id + "/progressbar.html";
        $.get(url, function(data) {
            elem_id = '#' + $(element).attr('id');
            $(element).replaceWith($(data.trim()));
            element = $(elem_id);
            set_progress_timeout(element);
        });
    };
}

function set_progress_timeout(element) {
    precision = $(element).data('precision');
    if (precision == 'DAY') {
        interval = 3600000;
    } else if (precision == 'HOUR') {
        interval = 60000;
    } else if (precision == 'MINUTE') {
        interval = 10000;
    } else {
        interval = 1000;
    }
    setTimeout(function(){
        refresh_progressbar(element);
    }, interval);
}

$(document).ready(function () {
    $('.roundprogressbar').each(function(){
        set_progress_timeout(this);
    });
});

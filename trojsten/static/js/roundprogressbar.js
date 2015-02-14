function refresh_progressbar(element) {
    console.log('refreshing progressbar', element);
    id = $(element).data('id');
    url = "/ulohy/ajax/" + id + "/progressbar.html";
    $.get(url, function(data) {
        console.log(element);
        elem_id = '#' + $(element).attr('id');
        $(element).replaceWith($(data.trim()));
        element = $(elem_id);
        console.log(element);
        set_progress_timeout(element);
    });
}

function set_progress_timeout(element) {
    console.log('timeout set', element);
    precision = $(element).data('precision');
    if (precision == 'DAY') {
        interval = 3600000;
    } else if (precision == 'HOUR') {
        interval = 60000;
    } else {
        interval = 10000;
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

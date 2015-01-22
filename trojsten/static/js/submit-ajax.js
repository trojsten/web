(function($)
{
    $(function()
    {
        /** Checks if submit finished testing in a loop, when the server
         * replies that the data is tested, calls callback with the
         * returned data */
        function poll_submit(id, callback) {
            $.get('/odovzdavanie/ajax/submit/' + id + '/info.json', function(data) {
                if (data.tested) {
                    callback(data);
                } else {
                    setTimeout(function() {
                        poll_submit(id, callback);
                    }, 1000);
                }
            });
        }

        $('.submit-untested').each(function() {
            var id = $(this).data('id');
            var that = this
            poll_submit(id, function(data) {
                $($(that).children()[1]).text('Dotestované');
                $($(that).children()[2]).text(data.response_verbose);
                $($(that).children()[3]).text(data.points);
                $(that).removeClass('info submit-untested').addClass(data.class);
            });
        });

        if ($('.submit-protocol').data('ready') == 'False') {
            var current_id = $('.submit-protocol').data('id');
            poll_submit(current_id, function() {
                $.get('/odovzdavanie/ajax/submit/' + current_id + '/protokol/', function(data) {
                    $('.submit-protocol').html(data);
                });
            });
        }
    });
})(jQuery);

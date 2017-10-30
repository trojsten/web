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
                    }, 10000);
                }
            });
        }

        $('.submit-untested').each(function() {
            var id = $(this).data('id');
            var that = this;
            var current_lang = $('body').data('language-code');
            poll_submit(id, function(data) {
                $($(that).children()[1]).text('Dotestované');
                $($(that).children()[2]).text(data.response_verbose);
                $($(that).children()[3]).text(data.points.toLocaleString(current_lang, {
                    minimumFractionDigits: 2,
                }));
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

        function download_reviewer_comment(id, callback) {
            $.get('/odovzdavanie/ajax/submit/' + id + '/komentar/', function(data) {
                callback(data);
            });
        }

        $('.comment-button').click(function(e) {
            e.preventDefault();
            var row = $(this).parent().parent()[0];
            var submit_id = $(this).data('id');
            if ($(this).hasClass('comment-hidden')) {
                $(this).removeClass('comment-hidden');
                var that = this;
                download_reviewer_comment(submit_id, function (data) {
                    $(row).after('<tr><td colspan="4">' + data + '</td></tr>');
                    $(that).addClass('comment-shown');
                    $(that).text('Schovaj komentár')
                    MathJax.Hub.Typeset();
                });
            } else if ($(this).hasClass('comment-shown')) {
                $(this).removeClass('comment-shown');
                $(row).next().remove();
                $(this).addClass('comment-hidden');
                $(this).text('Pozri komentár')
            }
        });

    });
})(jQuery);

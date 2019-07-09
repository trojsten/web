(function($)
{
    $(function()
    {
        var elements = [
            "input#id_corr_street",
            "input#id_corr_town",
            "input#id_corr_postal_code",
            "select#id_corr_country"
        ];

        var show_address = function() {
            for (var el in elements) {
                $(elements[el]).parent().parent().show();
            }
        };

        var hide_address = function() {
            console.log("hiding");
            for (var el in elements) {
                $(elements[el]).parent().parent().hide();
            }
        };

        $("input[name=mailing_option]").click(function() {
            $(this).val() == "O" ? show_address() : hide_address();
        });

        $("input[name=mailing_option]:checked").val() == "O" ? show_address() : hide_address();
    });
})(jQuery);

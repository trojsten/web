(function($)
{
    $(function()
    {
        var elements = [
            "input#id_corr_street",
            "input#id_corr_town",
            "input#id_corr_postal_code",
            "input#id_corr_country"
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

        $("input#id_mailing_option_0").click(function() {
            this.checked ? hide_address() : show_address();
        });

        $("input#id_mailing_option_1").click(function() {
            this.checked ? hide_address() : show_address();
        });

        $("input#id_mailing_option_2").click(function() {
            this.checked ? show_address() : hide_address();
        });

        if (!document.getElementById('id_mailing_option_2').checked) hide_address();
    });
})(jQuery);

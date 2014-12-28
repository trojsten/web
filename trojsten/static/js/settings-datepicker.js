(function($)
{
    $(function()
    {
        var elem = "input#id_birth_date";
        $(elem).datetimepicker({
            language: 'sk',
            pickTime: false,
        });
        $(elem).attr("autocomplete", "off");
    });

})(jQuery);

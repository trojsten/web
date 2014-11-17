(function($)
{
    $(function()
    {
        var elem = "input#id_birth_date";
        $(elem).datepicker({
            dateFormat: "dd.mm.yy",
            changeMonth: true,
            changeYear: true,
            yearRange: "1930:-6y"
        });
    });

})(jQuery);

(function($)
{
    $(function()
    {
        $("input[name=going]").change(function() {
            if ($("input[name=going]:checked").val().toLowerCase() == 'true' )
                $(".hidable_field").show();
            else
                $(".hidable_field").hide();
        });
    });
})(jQuery);

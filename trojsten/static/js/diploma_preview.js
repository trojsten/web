(function($)
{
    $(function()
    {
        $(document).ready(function () {
            console.log("WHYYYY")
        });

        $("#form").on({
            loaded: function () {
                console.log("Loaded")
            }
        });

        $("#id_template").on({
            change: function () {
                console.log("changed")
            }
        });

        var input = document.createElement("input");
        input.setAttribute("type", "hidden");
        input.setAttribute("name", "name_you_want");
        input.setAttribute("value", "value_you_want");
        document.getElementById("form").appendChild(input);
    });
})(jQuery);
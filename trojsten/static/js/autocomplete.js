// This lives at http://jsfiddle.net/koniiiik/NyaWw/
(function($)
{
    $(function()
    {
        var related_name = 'autocomplete_related_select';
        // Create required helper text inputs for all autocomplete selects.
        $('select.autocomplete').each(function()
        {
            var new_input = $('<input type="text" class="autocomplete_text"></input>');
            $(this).hide();
            $(this).after(new_input);
            new_input = $(this).next();
            new_input.data(related_name, $(this));
            // The pre-selected option's label will be shown initially.
            new_input.val($(this).children('option:selected').text());
        });

        // Set up the autocomplete widget.
        $('.autocomplete_text').autocomplete(
        {
            // We filter the list of all options' latinized labels and send
            // their corresponding values to the response callback.
            source: function(request, response)
            {
                var term = request.term.latinize();
                var pattern = new RegExp($.ui.autocomplete.escapeRegex(term), 'i');
                var data = [];
                var related_select = this.element.data(related_name);
                related_select.children('option').each(function()
                {
                    var latinized = $(this).data('latinized_label');
                    if (pattern.test(latinized))
                    {
                        data.push(
                        {
                            label: $(this).text(),
                            value: $(this).attr('value'),
                        });
                    }
                });
                response(data);
            },

            // Select the appropriate option in the hidden <select> and display
            // its label in the text input.
            select: function(event, ui)
            {
                $(this).data(related_name).val(ui.item.value);
                $(this).val(ui.item.label);
                return false;
            },

            // Display the appropriate label instead of value in the text field
            // when a different menu item has been focused using the keyboard.
            focus: function(event, ui)
            {
                $(this).val(ui.item.label);
                return false;
            },
        });

        // When the text input loses focus, display the currently selected value.
        $('.autocomplete_text').on('blur', function(event, ui)
        {
            var related_select = $(this).data(related_name);
            $(this).val(related_select.children('option:selected').text());
        });

        // Precompute the latinized label of each option so we don't have to
        // call latinize each time the list is filtered.
        $('select.autocomplete').children('option').each(function()
        {
            var text = $(this).text();
            $(this).data('latinized_label', text.latinize());
        });
    });
})(jQuery);

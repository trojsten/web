ksp_login.jQuery(function($)
{
    // Apply js-dependent CSS.
    $('.ksp_login_provider_list').addClass('ksp_login_provider_list_js');

    var show_element = function(elem, callback)
    {
        $(elem).slideDown({
            duration: 'fast',
            complete: callback,
        });
    };

    var hide_element = function(elem, callback)
    {
        $(elem).slideUp({
            duration: 'fast',
            complete: callback,
        });
    };

    var simple_provider_action = function(e)
    {
        // Stop propagation to prevent Bootstrap from closing the dropdown
        // this might be in.
        e.stopPropagation();
        $(this).siblings('form').submit();
    };

    var clear_selected_input_provider = function()
    {
        hide_element('.ksp_login_selected_input_provider', function()
        {
            hide_element($(this));
        });
        $('.ksp_login_selected_provider_button')
            .removeClass('ksp_login_selected_provider_button');
    };

    var input_provider_action = function(e)
    {
        // Stop propagation to prevent Bootstrap from closing the dropdown
        // this might be in.
        e.stopPropagation();
        var myself = $(this);
        if (myself.hasClass('ksp_login_selected_provider_button'))
        {
            clear_selected_input_provider();
            return;
        }
        clear_selected_input_provider();
        myself.addClass('ksp_login_selected_provider_button');
        var form = myself.siblings('form');
        form.addClass('ksp_login_selected_input_provider');
        form.hide();
        show_element(form);
    };

    var more_options_click = function()
    {
        // We have to use global JQuery here, because bootsrap adds .modal method to it
        jQuery('#ksp_login_modal_box').modal('show');
        return false;
    }

    // We have to directly bind the handlers to the elements themselves;
    // if we bind them to document, they get called after the Bootstrap
    // dropdown they reside in is closed.
    $('.ksp_login_provider_list > .provider_simple > a').on(
        'click',
        simple_provider_action
    );
    $('.ksp_login_provider_list > .provider_with_input > a').on(
        'click',
        input_provider_action
    );

    $('.ksp_login_more').on('click', more_options_click);

    // If the bootstrap dropdown JS is loaded in the global jQuery object,
    // prevent following links in the navbar dropdown button.
    if (window.$.fn.dropdown !== undefined)
    {
        $('#login-dropdown a').on('click', function(e)
        {
            e.preventDefault();
        });
    }
})

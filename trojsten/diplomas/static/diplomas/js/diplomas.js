(function($)
{

    let fields = JSON.parse(template_fields.replace(/&quot;/g,'"'));

    let memory_dict = {};

    function refresh_form() {
        var current_template = document.getElementById("id_template").value;
        var current_fields = fields[current_template];

        $('#dummy_form').find('input').each(function(i, component) {
            memory_dict[component.name] = component.value;
        });

        $("#fields_list").html(current_fields.join(', '));

        var container = document.getElementById("dummy_form");
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }

        $.each(current_fields, function (index, field_name) {

            var label = document.createElement('label');
            label.setAttribute('for', 'id_' + field_name);
            label.innerHTML = field_name;
            label.setAttribute('class', 'control-label col-sm-4 col-lg-4');

            var input = document.createElement("input");
            input.setAttribute("type", "text");
            input.setAttribute('id', 'id_' + field_name);
            input.setAttribute("name", field_name);
            var value = field_name in memory_dict ? memory_dict[field_name] : "";
            input.setAttribute("value", value);
            input.className = "form-control";

            var input_container = document.createElement("div");
            input_container.setAttribute('class', 'col-sm-4 col-lg-4');
            input_container.appendChild(input);

            var container = document.createElement("div");
            container.className = "form-group";
            container.appendChild(label);
            container.appendChild(input_container);

            document.getElementById("dummy_form").appendChild(container);
        });

        $.get("./" + current_template + '/sources/', function( data ) {
            $( "#sources_container" ).html( data );
        });

        document.getElementById("preview_image").src = "./" + current_template + '/preview/';
        document.getElementById("preview_image").setAttribute('alt', "./" + current_template + '/preview/')
    }

    function serialize_single_form(){
        let d = {};
        $("#dummy_form").find('input').each(function (i) {
           d[$(this).attr('name')] = $(this).val()
        });
        return JSON.stringify([d]);
    }

    window.set_editor_content = function(content){
        window.editor.setValue(content);
    };

    $(document).ready(function(){

        $("#form_submit_single").on({
            click: function () {
                document.getElementById("id_participants_data").value = serialize_single_form()
            }
        });
        $("#form_submit_multiple").on({
            click: function () {
                document.getElementById("id_participants_data").value = window.editor.getValue();
            }
        });

        $("#id_template").on({
            change: function () {
                refresh_form();
            }
        });

        $.get("./tutorial/", function( data ) {
            var el = document.createElement( 'html' );
            el.innerHTML = data;
            var content = el.getElementsByClassName('main-content')[0];
            if (content !== undefined){
                content.className = '';
                $("#tutorial_container" ).html(content)
            }
            else $("#tutorial_container" ).html( data );
        });

        refresh_form();
    });
})(jQuery);

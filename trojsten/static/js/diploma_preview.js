(function($)
{

    let fields = JSON.parse(template_fields.replace(/&quot;/g,'"'));

    let memory_dict = {};

    function refresh_form() {
        var current_template = document.getElementById("id_template").value;
        var current_fields = fields[current_template];


        $('div', $('#dummy_form')).each(function () {
            memory_dict[this.children[1].name] = this.children[1].value;
        });

        var container = document.getElementById("dummy_form");
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }

        $.each(current_fields, function (index, field_name) {

            var input = document.createElement("input");
            input.setAttribute("type", "text");
            input.setAttribute('id', 'id_' + field_name);
            input.setAttribute("name", field_name);
            var value = field_name in memory_dict ? memory_dict[field_name] : "";
            input.setAttribute("value", value);

            var label = document.createElement('label');
            label.setAttribute('for', 'id_' + field_name);
            label.innerHTML = field_name;
            label.setAttribute("style","width:100px");

            var input_container = document.createElement("div");
            input_container.className = "form-group";
            input_container.appendChild(label);
            input_container.appendChild(input);
            input_container.setAttribute('style', 'margin-top:5px');

            document.getElementById("dummy_form").appendChild(input_container);
        });

        $.get("./" + current_template + '/sources/', function( data ) {
          $( "#sources_container" ).html( data );
        });

        document.getElementById("preview_image").src = "./" + current_template + '/preview/';
        document.getElementById("preview_image").setAttribute('alt', "./" + current_template + '/preview/')
    }

    function serialize_single_form(){
        let d = {};
        document.getElementById("dummy_form").childNodes.forEach(function(item){
            d[item.childNodes[1].name] = item.childNodes[1].value;
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
        refresh_form();
    });
})(jQuery);
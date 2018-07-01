(function($)
{
    $(function()
    {
        $(document).ready(function(){

            $("#id_participants_data").on({
                change: function () {
                    var f = document.getElementById("id_participants_data").files[0];

                    var fileReader = new FileReader();
                    fileReader.onload = function(fileLoadedEvent){
                        var textFromFileLoaded = fileLoadedEvent.target.result;
                        window.editor.setValue(textFromFileLoaded);
                    };
                    fileReader.readAsText(f, "UTF-8");
                }
            });

            refresh_form();
        });

        let fields = JSON.parse(template_fields.replace(/&quot;/g,'"'));

        function refresh_form() {
            var current_fields = fields[document.getElementById("id_template").value];

            var container = document.getElementById("dummy_form");
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }

            $.each(current_fields, function (index, field_name) {
                var input = document.createElement("input");
                input.setAttribute("type", "text");
                input.setAttribute('id', 'id_' + field_name);
                input.setAttribute("name", field_name);
                input.setAttribute("value", "");
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

            document.getElementById("preview_link").setAttribute('href', "./" + document.getElementById("id_template").value);
            document.getElementById("preview_image").src = "./" + document.getElementById("id_template").value;
            document.getElementById("preview_image").setAttribute('alt', "./" + document.getElementById("id_template").value)
        }

        function serialize_data(){
            let d = {};
            document.getElementById("dummy_form").childNodes.forEach(function(item){
                d[item.childNodes[1].name] = item.childNodes[1].value;
            });
            return JSON.stringify([d]);
        }

        $("#form").on({
            submit: function(){
                document.getElementById("id_single_participant_data").value = serialize_data();
            }
        });

        $("#id_template").on({
            change: function () {
                refresh_form();
                serialize_data();
            }
        });

    });
})(jQuery);
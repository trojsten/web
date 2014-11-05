
var submit_url = ""

$('#valueForm').submit( function(){
    $("#valueForm :input").prop("disabled", true);
	$.ajax({
        type: 'POST',
        url: submit_url,
        data: JSON.stringify({input:$('#value').val()}),
        headers: {
            "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
        }
    }).done(function(data) {

        if(data.refresh){
            location.reload();
            return;
        }

        $("#valueForm :input").prop("disabled", false);
        document.getElementById("value").focus();
        $("#value").val("");

        $('.results').scrollTop(0);

        $("#try-count").text(data.try_count);
        add_row(data.input, data.output, data.solved);
        submit_url = data.next_url;

    }).error(function(err) {
        $("#valueForm :input").prop("disabled", false);
        document.getElementById("value").focus();
    });
    return false;
});

function add_row(input, output, solved){
    $('#resultsTable').prepend(
        '<tr><td class="t-input">'+
        input+
        '</td><td class="t-output"><code class="'+
        (solved ? 'solved' : '')+
        '">'+
        output+
        '</code></td></tr>'
    );
}

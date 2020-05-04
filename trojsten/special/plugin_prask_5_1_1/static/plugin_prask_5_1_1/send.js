
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

        // console.log('volam', data.examples_match, data.examples_neg);
        change_table(data.examples_match, data.examples_neg);
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
        (solved ? 'Správne' : 'Nesprávne') +
        '</code></td></tr>'
    );
}

function change_table(examples_match, examples_neg){
  $("#match").find("tbody").empty();
  $("#neg").find("tbody").empty();

  // console.log('volam', examples_match, examples_neg)
  $('#match').append('<tr><th bgcolor="#8b008b"> Regexu vyhovujúce </th></tr>');
  $('#neg').append('<tr><th bgcolor="#8b008b"> Regexu nevyhovujúce </th></tr>');

  var i;
  for (i = 0; i < examples_match.length; i++) {
    word_ = examples_match[i][0];
    color_ = examples_match[i][1];
    $('#match').append(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ +
        '</th></tr>'
    );
  }

  for (i = 0; i < examples_neg.length; i++) {
    word_ = examples_neg[i][0];
    color_ = examples_neg[i][1];
    $('#neg').append(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ +
        '</th></tr>'
    );
  }
}

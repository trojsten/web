
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

// function change_table(match, neg, examples_match, examples_neg){
//   // $('#match').clear();
//   // $('#neg').clear();
//   $("#match").find("tbody").empty();
//   $("#neg").find("tbody").empty();
//
//
//   var i;
//   for (i = 0; i < match.length; i++) {
//     word_ = match[i][0];
//     color_ = match[i][1];
//     $('#match').prepend(
//         '<tr><th bgcolor="' + color_ + '">'+
//         word_ +
//         '</th></tr>'
//     );
//   }
//
//   for (i = 0; i < neg.length; i++) {
//     word_ = neg[i][0];
//     color_ = neg[i][1];
//     $('#neg').prepend(
//         '<tr><th bgcolor="' + color_ + '">'+
//         word_ + color_ +
//         '</th></tr>'
//     );
//   }
// }

function change_table(examples_match, examples_neg){
  $("#match").find("tbody").empty();
  $("#neg").find("tbody").empty();

    $('#match').prepend(
        '<tr><th>'+
        examples_match +
        '</th></tr>'
    );

    word_ = examples_match[0][0];
    color_ = examples_match[0][1];
    $('#match').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ +
        '</th></tr>'
    );
  var i;
  for (i = 0; i < examples_match.length; i++) {
    word_ = examples_match[i][0];
    color_ = examples_match[i][1];
    $('#match').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ +
        '</th></tr>'
    );
  }

  for (i = 0; i < examples_neg.length; i++) {
    word_ = examples_neg[i][0];
    color_ = examples_neg[i][1];
    $('#neg').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ + color_ +
        '</th></tr>'
    );
  }
}

function change_table_start(examples_match, examples_neg){
  $("#match").find("tbody").empty();
  $("#neg").find("tbody").empty();


  var i;
  for (i = 0; i < examples_match.length; i++) {
    word_ = examples_match[i][0];
    color_ = examples_match[i][1];
    $('#match').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ + color_ +
        '</th></tr>'
    );
  }

  for (i = 0; i < examples_neg.length; i++) {
    word_ = examples_neg[i][0];
    color_ = examples_neg[i][1];
    $('#neg').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        'aaa' + Math.floor(Math.random() * 10) +
        '</th></tr>'
    );
  }
}


function change_table_next(examples_match, examples_neg){
  $("#match").find("tbody").empty();
  $("#neg").find("tbody").empty();


    $('#match').prepend(
        '<tr><th>'+
        examples_match +
        '</th></tr>'
    );

  var i;
  for (i = 0; i < examples_match.length; i++) {
    word_ = examples_match[i][0];
    color_ = examples_match[i][1];
    $('#match').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        word_ + 8 +
        '</th></tr>'
    );
  }

  for (i = 0; i < examples_neg.length; i++) {
    word_ = examples_neg[i][0];
    color_ = examples_neg[i][1];
    $('#neg').prepend(
        '<tr><th bgcolor="' + color_ + '">'+
        'aaa' + Math.floor(Math.random() * 10) +
        '</th></tr>'
    );
  }
}
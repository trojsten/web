var submit_url = "";
var already_solved = false;

$('#valueForm').submit(function () {
    $("#valueForm :input").prop("disabled", true);
    $.ajax({
        type: 'POST',
        url: submit_url,
        data: JSON.stringify({input: $('#value').val()}),
        headers: {
            "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
        }
    }).done(function (data) {

        // if(data.refresh){
        // }

        $("#last_input").text(data.last_input);

        $("#valueForm :input").prop("disabled", false);
        document.getElementById("value").focus();
        $("#value").val("");

        $('.results').scrollTop(0);

        $("#try-count").text(data.try_count);
        add_row(data.input, data.output, data.solved);
        submit_url = data.next_url;

        change(data.examples_match, data.examples_neg,
            data.solved, data.solved_before, data.try_count, data.input, data.last_input);

    }).error(function (err) {
        $("#valueForm :input").prop("disabled", false);
        document.getElementById("value").focus();
    });
    return false;
});

function add_row(input, output, solved) {

    $('#resultsTable').prepend(
        '<tr><td class="t-input">' +
        input +
        '</td><td class="t-output"><code class="' +
        (solved ? 'solved' : '') +
        '">' +
        (solved ? 'Správne' : 'Nesprávne') +
        '</code></td></tr>'
    );
}

function change(examples_match, examples_neg, solved, solved_before, try_count, input, last_input) {
    console.log(typeof solved);
    change_table(examples_match, examples_neg);
    change_text(solved, solved_before, try_count, input, last_input);
}

function change_table(examples_match, examples_neg) {

    $("#match").find("tbody").empty();
    $("#neg").find("tbody").empty();

    $('#match').append('<tr><th bgcolor="#8b008b"> Regexu vyhovujúce </th></tr>');
    $('#neg').append('<tr><th bgcolor="#8b008b"> Regexu nevyhovujúce </th></tr>');

    var i;
    for (i = 0; i < examples_match.length; i++) {
        word_ = examples_match[i][0];
        color_ = examples_match[i][1];
        $('#match').append(
            '<tr><th bgcolor="' + color_ + '">' +
            word_ +
            '</th></tr>'
        );
    }

    for (i = 0; i < examples_neg.length; i++) {
        word_ = examples_neg[i][0];
        color_ = examples_neg[i][1];
        $('#neg').append(
            '<tr><th bgcolor="' + color_ + '">' +
            word_ +
            '</th></tr>'
        );
    }

    document.getElementById("task_state").innerHTML = "";
    $('#task_state').append('Vytvor regex, ktorý vyhovuje/nevyhovuje slovám z tabuliek.')
}

function change_text(solved, solved_before, try_count, input, last_input) {
    // $("#task_state").find("body").empty();
    // $("#task_state") = '';
    document.getElementById("task_state").innerHTML = "";

    if (solved || solved_before) {
        $('#task_state').append('Gratulujeme!\n' +
            'Tvoj regex <code id="good" class="solved">' + last_input + '</code>\n' +
            'je správny! Zvládol si to na <span id="try-count">' + try_count + '.</span>\n' +
            'pokus');
    } else {
        if (try_count === 0)  {
            $('#task_state').append('Vytvor regex, ktorý vyhovuje/nevyhovuje slovám z tabuliek.');
        } else {
            $('#task_state').append('Regex <code id="last_input">' + input + '</code> nie je správna odpoveď.\n' +
                '<br/>Počet doterajších pokusov: <span id="try-count">' + try_count + '</span>.')
        }
    }
}


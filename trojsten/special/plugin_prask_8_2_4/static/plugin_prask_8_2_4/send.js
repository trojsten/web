
var submit_url = ""
var forbidden_words = ''
var load_anim = `
<p>
    <span class="skeleton-box" style="width:80%;"></span>
    <span class="skeleton-box" style="width:90%;"></span>
    <span class="skeleton-box" style="width:83%;"></span>
    <span class="skeleton-box" style="width:80%;"></span>
</p>
`

$('#valueForm').submit(function(e){
    e.preventDefault();
    $("#value").prop("disabled", true);
    $('#result').html(load_anim);
	$.ajax({
        type: 'POST',
        url: submit_url,
        data: JSON.stringify({input:$('#value').val()}),
        headers: {
            "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
        }
    }).done(function(data) {
        data = JSON.parse(data);
        console.log(data);
        if(data.refresh){
            location.reload();
            return;
        }
        // add_row(data.output);
        $('#result').html(data.text);
    }).error(function(err) {
        alert(JSON.stringify(err));
        $('#result').text('')
    }).always(() => {
        $("#value").prop("disabled", false);
        document.getElementById("value").focus();
    });
    return false;
});

$(document).ready(function() {
    $("textarea").each(function () {
        this.setAttribute("style", "height:" + (this.scrollHeight) + "px;overflow-y:hidden;");
    }).on("input", function () {
        this.style.height = 0;
        this.style.height = (this.scrollHeight) + "px";
        const text = $('#value');
        const submit = $('#submit');
        if(forbidden_words == '') return;
        for (const word of forbidden_words.split(',')) {
            if (text.val().toLowerCase().match(word)){
                text.addClass('wrong');
                submit.prop('disabled', true);
                break;
            }
            else {
                text.removeClass('wrong');
                submit.prop('disabled', false);
            }   
        }        
    });
});

// function add_row(input, output, solved){
//     $('#resultsTable').prepend(
//         '<tr><td class="t-input">'+
//         input+
//         '</td><td class="t-output"><code class="'+
//         (solved ? 'solved' : '')+
//         '">'+
//         output+
//         '</code></td></tr>'
//     );
// }

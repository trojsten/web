$('#hintForm').submit( function(e) {
  e.preventDefault();
  if (!confirm("Pozor, zobrazením nápovedy stratíš tretinu bodov z celkového počtu bodov za vyriešený level. Nie je to ale nič hrozné, takže sa neboj nápovedy používať ak sa zasekneš!")) return false;
  $.ajax({
        type: 'POST',
        url: HINT_URL,
        headers: {
            "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
        }
    }).done(function(data) {
      $('#hintText').text(data.hint);
    }).fail(function(err) {
        alert("error");
    });
    return false;
});
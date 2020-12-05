$('#hintForm').submit( function(e) {
  e.preventDefault();
  if (!confirm("Pozor, po zobrazení nápovedy môžeš za level získať najviac 7 bodov z pôvodných 10. Nie je to ale nič hrozné, takže sa neboj nápovedy používať ak sa zasekneš!")) return false;
  $.ajax({
        type: 'POST',
        url: HINT_URL,
    }).done(function(data) {
      $('#hintText').text(data.hint);
    }).fail(function(err) {
        alert("error");
    });
    return false;
});

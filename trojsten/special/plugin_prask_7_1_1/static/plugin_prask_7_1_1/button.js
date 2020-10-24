$('#buttonForm').submit( function(e) {
    e.preventDefault();
    $.ajax({
          type: 'POST',
          url: BUTTON_SUBMIT_URL,
      }).done(function(data) {
        $('#password').text(data.password);
      }).fail(function(err) {
          alert("error");
      });
      return false;
  });

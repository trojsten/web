$('#buttonForm').submit( function(e) {
    e.preventDefault();
    $.ajax({
          type: 'POST',
          url: BUTTON_SUBMIT_URL,
          headers: {
              "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
          }
      }).done(function(data) {
        $('#password').text(data.password);
      }).fail(function(err) {
          alert("error");
      });
      return false;
  });
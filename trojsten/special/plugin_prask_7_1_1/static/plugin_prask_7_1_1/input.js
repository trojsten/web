$('#inputForm').submit( function(e) {
    e.preventDefault();
    $.ajax({
          type: 'POST',
          url: INPUT_SUBMIT_URL,
          data: {
            schnitzels:$('#schnitzels').val(),
          },
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
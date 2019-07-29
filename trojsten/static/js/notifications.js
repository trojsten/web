(function () {
  const icons = {
    'submit_reviewed': 'thumbs-up',
    'contest_new_round': 'plus',
  }

  const original_title = $('title').text()

  let update_data = () => {
    $.getJSON(window.TROJSTEN_NOTIFY_URL, (data) => {
      let content = []

      data.objects.forEach(notification => {
        content.push('<li role="presentation"><a href="'+window.TROJSTEN_NOTIFY_GOTO+notification.pk+'"><i class="glyphicon glyphicon-' + (icons[notification.type] || 'info-sign') + '"></i> ' + notification.message + '</a></li>');
      })

      $('#notification-box-content').html(content.join(''))

      if (data.total_count > 0) {
        $('#notification-box-number').show()
        $('#notification-box-number').text(data.total_count)
        $('title').text('(' + data.total_count + ') ' + original_title)
      } else {
        $('#notification-box-number').hide()
        $('#notification-box-content').html('<li role="presentation"><a href="#">Žiadne notifikácie!</a></li>')
        $('title').text(original_title)
      }
    })
  }

  update_data()
  setInterval(update_data, 5*60*1000)
})()

(function () {
  const icons = {
    'SubmitReviewed': 'thumbs-up',
    'RoundStarted': 'plus',
  }

  const original_title = $('title').text()


  let update_data = () => {
    $.getJSON(window.TROJSTEN_NOTIFY_LIST, (data) => {
      let content = []

      data.notifications.forEach(notification => {
        content.push('<li role="presentation"><a href="'+notification.url+'"><i class="glyphicon glyphicon-' + (icons[notification.type] || 'info-sign') + '"></i> ' + notification.message + '</a></li>');
      })

      $('#notification-box-content').html(content.join(''))

      if (data.unread > 0) {
        $('#notification-box-number').show()
        $('#notification-box-number').text(data.unread)
        $('title').text('(' + data.unread + ') ' + original_title)
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

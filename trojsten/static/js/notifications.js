(function () {
  const original_title = $('title').text()

  let update_data = () => {
    $.getJSON(window.TROJSTEN_NOTIFY_LIST_URL, (data) => {
      let content = []

      data.notifications.forEach(notification => {
        content.push('<li role="presentation"><a href="'+notification.url+'"><i class="glyphicon glyphicon-' + (data.icons[notification.channel] || 'info-sign') + '"></i> ' + notification.message + '</a></li>');
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

      $('#notification-box-content').append('<li role="presentation" class="divider"></li>')

      if (data.unread > 0) {
        $('#notification-box-content').append('<li role="presentation" id="notifications-read-all"><a href="#"><i class="glyphicon glyphicon-eye-open"></i> Označiť všetky za prečítané</a></li>')
        $("#notifications-read-all").click(() => {
          $.post(window.TROJSTEN_NOTIFY_READ_ALL_URL, update_data)
        })
      }

      $('#notification-box-content').append('<li role="presentation"><a href="/ucet/#notifications"><i class="glyphicon glyphicon-cog"></i> Nastavenia notifikácií</a></li>')
    })
  }

  update_data()
  setInterval(update_data, 5*60*1000)
})()

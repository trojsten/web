(function () {
  const icons = {
    'submit_reviewed': 'thumbs-up',
    'contest_new_round': 'plus',
  }

  const original_title = $('title').text()
  let last_count = -1;

  let update_data = () => {
    $.getJSON('/wiki/notify/json/get', (data) => {
      let content = []

      data.objects.forEach(notification => {
        content.push('<li role="presentation"><a href="/wiki/notify/goto/'+notification.pk+'"><i class="glyphicon glyphicon-' + (icons[notification.type] || 'info-sign') + '"></i> ' + notification.message + '</a></li>');
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

      if (last_count != -1 && last_count < data.total_count && Notification.permission == 'granted') {
        let diff = data.total_count - last_count

        if (diff == 1) {
          new Notification('Trojsten', {
            body: data.objects[data.objects.length - 1].message,
            icon: window.TROJSTEN_ICON
          })
        } else {
          let sklon = 'nových notifikácií'
          if (diff < 5) {
            sklon = 'nové notifikácie'
          }

          new Notification('Trojsten', {
            body: 'Máš ' + diff + ' ' + sklon + '!',
            icon: window.TROJSTEN_ICON
          })
        }
      }

      last_count = data.total_count
    })
  }

  update_data()
  setInterval(update_data, 5*60*1000)

  Notification.requestPermission()
})()

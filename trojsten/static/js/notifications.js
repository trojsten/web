(function () {
  const icons = {
    'submit_reviewed': 'thumbs-up'
  }

  let update_data = () => {
    $.getJSON('/wiki/notify/json/get', (data) => {
      let content = []

      data.objects.forEach(notification => {
        content.push('<li role="presentation"><a href="/wiki/notify/goto/'+notification.pk+'"><i class="glyphicon glyphicon-' + (icons[notification.type] || 'info-sign') + '"></i> ' + notification.message + '</a></li>');
      })

      $("#notification-box-content").html(content.join(''))
      if (data.total_count > 0) {
        $("#notification-box-number").show()
        $("#notification-box-number").text(data.total_count)
      } else {
        $("#notification-box-number").hide()
        $("#notification-box-content").html('<li role="presentation"><a href="#">Žiadne notifikácie!</a></li>')
      }
    })
  }

  update_data()

  setInterval(update_data, 10*60*1000)
})()

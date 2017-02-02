// Javascript to enable link to tab
$(document).ready(function() {
  var url = document.location.toString();
  if (url.match('#')) {
      $('a[role="tab"][href="#' + url.split('#')[1] + '"]').tab('show');
  }
}); 

// Change hash for page-reload
$('a[role="tab"]').on('shown.bs.tab', function (e) {
    window.location.hash = e.target.hash;
})

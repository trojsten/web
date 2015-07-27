if($.fn.on) {
  // jQuery 1.7+
  $('body').on('click', '.comment-reply-link', scrollToCommentReply);
}
else {
  $('.comment-reply-link').live('click', scrollToCommentReply);
}

function scrollToCommentReply(id, speed){
  setTimeout(
    function(){
      scrollToElement($('.js-comments-form'), 1000, 60);
    }, 200);
}

function scrollToElement( $element, speed, offset ){
  if( $element.length )
    $('html, body').animate( {scrollTop: $element.offset().top - (offset || 0) }, speed || 1000 );
}

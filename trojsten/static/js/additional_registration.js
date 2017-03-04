function switch_competition_participation(elem) {
  var url = "/api/people/switch_contest_participation/";
  var element = $(elem);
  $.post(url, {
    competition: element.data("competition"),
    value: element.attr("checked") ? true : false
  });
}

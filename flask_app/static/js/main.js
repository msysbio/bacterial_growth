$.fn.log = function() {
  console.log($(this));
  return this;
}

$(document).ready(function() {
  let currentPath = window.location.pathname;

  $('.nav-links a').each(function() {
    let $link = $(this);
    let $li   = $link.parents('li');
    let href  = $link.attr('href');

    if (href == '/' && currentPath == '/') {
      $li.addClass('current-path');
    } else if (href != '/' && currentPath.startsWith(href)) {
      $li.addClass('current-path');
    }
  });

  $('#page-sidebar .close-sidebar a').log().on('click', function(e) {
    e.preventDefault();

    $(':root').css('--sidebar-width', '0px');
    $('#main .open-sidebar').css('width', '50px');
  });

  $('#main .open-sidebar a').on('click', function(e) {
    e.preventDefault();

    $(':root').css('--sidebar-width', '340px');
    $('#main .open-sidebar').css('width', '0px');
  });
});

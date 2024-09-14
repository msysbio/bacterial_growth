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

  $('#page-sidebar .close-sidebar a').on('click', function(e) {
    e.preventDefault();

    $(':root').css('--sidebar-width', '0px');
    $('#main .open-sidebar').css('width', '50px');

    let transitionLengthMs = parseInt($(':root').css('--transition-length'), 10);
    setTimeout(function() {
      $(document).trigger('x-sidebar-resize')
    }, transitionLengthMs + 1);
  });

  $('#main .open-sidebar a').on('click', function(e) {
    e.preventDefault();

    $(':root').css('--sidebar-width', '340px');
    $('#main .open-sidebar').css('width', '0px');

    let transitionLengthMs = parseInt($(':root').css('--transition-length'), 10);
    setTimeout(function() {
      $(document).trigger('x-sidebar-resize')
    }, transitionLengthMs + 1);
  });

  $('.js-tabs .tab-headers span').on('click', function(e) {
    e.preventDefault();

    let $clickedHeader = $(this);
    let $container = $clickedHeader.parents('.js-tabs')

    let $headers = $container.find('.tab-headers span');
    let $bodies = $clickedHeader.parents('.js-tabs').find('.tab-body');

    $headers.removeClass('active');
    $clickedHeader.addClass('active');

    let clickedIndex = $headers.index(this);
    $bodies.removeClass('active');
    $($bodies[clickedIndex]).addClass('active');
  });
});

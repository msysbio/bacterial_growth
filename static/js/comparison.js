$(document).ready(function() {
  $('.comparison-page').each(function() {
    let $page = $(this);

    update_chart($page.find('.data-container'));

    $page.on('change', '.js-target', function() {
      let scrollPosition = $(document).scrollTop();

      let $target = $(this);
      let $container = $target.parents('.data-container');

      update_chart($container);
    });

    function update_chart($container) {
      let $form  = $container.find('form');
      let $chart = $container.find('.chart');
      let width  = Math.floor($chart.width());

      $.ajax({
        url: `/comparison/chart?width=${width}`,
        dataType: 'html',
        data: $form.serializeArray(),
        success: function(response) {
          $chart.html(response);
          $(document).scrollTop(scrollPosition);
        }
      })
    }
  });
});

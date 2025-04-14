$(document).ready(function() {
  $('.comparison-page').each(function() {
    let $page = $(this);

    update_chart($page.find('.data-container'));

    $page.on('change', '.js-target', function() {
      let scrollPosition = $(document).scrollTop();

      let $target    = $(this);
      let $container = $target.parents('.data-container');
      let target     = $target.prop('name');

      if ($target.is(':checked')) {
        // uncheck all others with the same name
        $page.find(`input[name="${target}"]`).each(function() {
          let $otherInput = $(this);
          if (!$target.is($otherInput)) {
            $otherInput.prop('checked', false);
          }
        });
      }

      update_chart($container, scrollPosition);
    });

    $(document).on('x-sidebar-resize', function() {
      $('.js-plotly-plot').each(function() {
        let $chart = $(this);
        let width = Math.floor($chart.parents('.chart').width());

        Plotly.relayout($chart[0], { 'width': width }, 0);
      });
    });

    function update_chart($container, scrollPosition) {
      let $form  = $container.find('form');
      let $chart = $container.find('.chart');
      let width  = Math.floor($chart.width());

      $.ajax({
        url: `/comparison/chart?width=${width}`,
        dataType: 'html',
        data: $form.serializeArray(),
        success: function(response) {
          $chart.html(response);

          if (scrollPosition) {
            $(document).scrollTop(scrollPosition);
          }
        }
      })
    }
  });
});

$(document).ready(function() {
  $('.study-visualize-page').each(function() {
    let $page = $(this);
    let studyId = $page.data('studyId')

    $page.find('.experiment-container').each(function(e) {
      let $container = $(this);

      if ($container.find('input[type=checkbox]:checked').length > 0) {
        $container.prop('open', true);
        let $form = $container.find('form');
        update_chart($form);
      }
    });

    $(document).on('x-sidebar-resize', function() {
      $('.js-plotly-plot').each(function() {
        let $chart = $(this);
        let width = Math.floor($chart.parents('.chart').width());

        Plotly.relayout($chart[0], { 'width': width }, 0);
      });
    });

    $page.on('change', 'form.chart-form', function(e) {
      let $form = $(e.currentTarget);
      update_chart($form);
    });

    $page.on('click', '.clear-chart', function(e) {
      e.preventDefault();

      let $link = $(e.currentTarget);
      let $container = $link.parents('.experiment-container');
      $container.find('input[type=checkbox]').prop('checked', false);

      update_chart($container.find('form'))
    });

    function update_chart($form) {
      let $experiment = $form.find('.experiment');
      let $chart      = $experiment.find('.chart');

      let width          = Math.floor($chart.width());
      let scrollPosition = $(document).scrollTop();

      $.ajax({
        url: `/study/${studyId}/visualize/chart?width=${width}`,
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

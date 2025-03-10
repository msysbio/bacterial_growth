$(document).ready(function() {
  $('.dashboard-page').each(function() {
    let $page = $(this);

    let urlParams = new URLSearchParams(window.location.search);
    let studyId = urlParams.get('studyId');

    $page.find('details.experiment-container').each(function(e) {
      $details = $(this);

      if ($details.find('input[type=checkbox]:checked').length > 0) {
        $details.prop('open', true);
        let $form = $details.find('form');
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
      let $details = $link.parents('details.experiment-container');
      $details.find('input[type=checkbox]').prop('checked', false);
      $details.prop('open', false);
    });

    function update_chart($form) {
      let $experiment = $form.find('.experiment');
      let $chart      = $experiment.find('.chart');

      let width          = Math.floor($chart.width());
      let scrollPosition = $(document).scrollTop();

      $.ajax({
        url: `/dashboard/chart?studyId=${studyId || ''}&width=${width}`,
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

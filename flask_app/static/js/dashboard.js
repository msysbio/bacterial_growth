$(document).ready(function() {
  let $page = $('.dashboard-page');

  let urlParams = new URLSearchParams(window.location.search);
  let studyId = urlParams.get('studyId');

  // $page.find('.chart-form').each(function() {
  //   let $form = $(this);
  //
  //   console.log($form.serializeArray());
  // });

  $page.on('change', 'form.chart-form', function(e) {
    let $form       = $(e.currentTarget);
    let $experiment = $form.parents('.experiment');
    let $chart      = $experiment.find('.chart');

    let width        = Math.floor($chart.width());
    let experimentId = $experiment.data('experimentId')

    $.ajax({
      url: `/dashboard/chart?studyId=${studyId || ''}&experimentId=${experimentId}&width=${width}`,
      dataType: 'html',
      data: $form.serializeArray(),
      success: function(response) {
        $chart.html(response);
      }
    })
  });
});

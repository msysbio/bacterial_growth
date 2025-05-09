$(document).ready(function() {
  $('.study-page').each(function() {
    let $page   = $(this);
    let studyId = $page.data('studyId');

    $page.on('change', '.js-technique-type', function() {
      updateMeasurementSubjects($(this).parents('form'));
    });

    updateMeasurementSubjects($page.find('.js-calculation-form'));

    $page.on('click', '.js-edit-trigger', function(e) {
      e.preventDefault();

      let $trigger        = $(this);
      let $result         = $trigger.parents('form').find('.js-result-container')
      let $chart          = $result.find('.js-chart-preview')
      let url             = $trigger.attr('href');
      let calculationType = $trigger.parents('form').find('input[name=type]').val()

      $page.find('.js-subject-row').removeClass('highlight');
      $trigger.parents('.js-subject-row').addClass('highlight');

      $.ajax({
        url: url,
        dataType: 'html',
        data: {
          'calculationType': calculationType,
          'width':           $chart.width(),
          'height':          $chart.height(),
        },
        success: function(response) {
          $result.html(response)
        },
      });
    });

    $page.on('submit', '.js-calculation-form', function(e) {
      e.preventDefault();
      let $form = $(e.currentTarget);

      $.ajax({
        url: $form.attr('action'),
        dataType: 'json',
        method: 'POST',
        data: $form.serializeArray(),
        success: function(response) {
          let calculationTechniqueId = response.calculationTechniqueId;
          let $result = $page.find('.js-calculation-result');

          function check() {
            $.ajax({
              url: `/study/${studyId}/calculations/${calculationTechniqueId}.json`,
              dataType: 'json',
              success: function(response) {
                if (!response.ready) {
                  $result.html('Calculating...');
                  setTimeout(check, 1000);
                  return;
                }

                if (!response.successful) {
                  $result.html('<span class="error">[error]</span>');
                  return;
                }

                $result.html("OK");
              }
            });
          }

          check();
        }
      })
    });

    function updateMeasurementSubjects($form) {
      let $techniqueSelect = $form.find('.js-technique-type');
      let techniqueId = $techniqueSelect.val();

      $form.find('[data-technique-id]').addClass('hidden')
      $form.find(`[data-technique-id=${techniqueId}]`).removeClass('hidden')
    }
  });
});

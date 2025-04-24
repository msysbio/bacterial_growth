$(document).ready(function() {
  $('.study-page').each(function() {
    let $page = $(this);

    $page.on('change', '.js-technique-type', function() {
      updateMeasurementSubjects($(this).parents('form'));
    });

    updateMeasurementSubjects($page.find('.js-calculation-form'));

    $page.on('click', '.js-preview-trigger', function() {
      let $button = $(this);
      let $preview = $button.parents('form').find('.js-preview')
      let url = $button.data('url');

      $page.find('.js-subject-row').removeClass('highlight');
      $button.parents('.js-subject-row').addClass('highlight');

      $.ajax({
        url: url,
        dataType: 'html',
        data: { 'width': $preview.width() },
        success: function(response) {
          $preview.html(response)
        },
      });
    });

    $page.on('submit', '.js-calculation-form', function(e) {
      e.preventDefault();
      let $form = $(e.currentTarget);

      $.ajax({
        url: `/study/${studyId}/calculations`,
        dataType: 'json',
        method: 'POST',
        data: $form.serializeArray(),
        success: function(response) {
          let taskId = response.taskId;
          let $result = $page.find('.js-calculation-result');

          function check() {
            $.ajax({
              url: `/study/${studyId}/calculations/${taskId}.json`,
              dataType: 'json',
              success: function(response) {
                if (!response.ready) {
                  $result.html('[<em>calculating...</em>]');
                  setTimeout(check, 1000);
                  return;
                }

                if (!response.successful) {
                  $result.html('<span class="error">[error]</span>');
                  return;
                }

                $result.html(response.value);
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

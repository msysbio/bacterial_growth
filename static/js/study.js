$(document).ready(function() {
  $('.study-page').each(function() {
    let $page       = $(this);
    let $compareBox = $(document).find('.js-compare-box')

    let studyId     = $page.data('studyId');
    let compareData = $compareBox.data('value');

    // TODO: a timestamp with a check on update?
    if (!compareData.targets) {
      compareData['targets'] = [];
    }

    if (compareData['targets'].length > 0) {
      $compareBox.removeClass('hidden');
    }

    let targetSet = new Set(compareData['targets']);

    $page.find('.js-compare-container').each(function() {
      let $container = $(this);
      if (!targetSet.has($container.data('targetIdentifier'))) {
        return;
      }

      $container.find('.js-uncompare').removeClass('hidden');
      $container.find('.js-compare').addClass('hidden');
      $container.parents('.js-table-row').addClass('highlight');
    });

    $page.on('click', '.js-compare a', function(e) {
      e.preventDefault();

      let $button    = $(this);
      let $wrapper   = $button.parents('.js-compare');
      let $container = $button.parents('.js-compare-container');

      let targetIdentifier = $container.data('targetIdentifier');

      updateCompareBox('add', targetIdentifier, function(compareData) {
        $compareBox.data('value', compareData);
        $compareBox.find('.js-target-count').text(compareData.targetCount);
        $compareBox.removeClass('hidden');

        // Hide "compare" button, show "uncompare" button
        $wrapper.addClass('hidden');
        $container.find('.js-uncompare').removeClass('hidden');

        // Highlight compared row
        $container.parents('.js-table-row').addClass('highlight');
      });
    });

    $page.on('click', '.js-uncompare a', function(e) {
      e.preventDefault();

      let $button    = $(this);
      let $wrapper   = $button.parents('.js-uncompare');
      let $container = $button.parents('.js-compare-container');

      let targetIdentifier = $container.data('targetIdentifier');

      updateCompareBox('remove', targetIdentifier, function(compareData) {
        $compareBox.data(compareData);
        let targetCount = compareData.targetCount;

        if (targetCount == 0) {
          $compareBox.addClass('hidden');
        } else {
          $compareBox.find('.js-target-count').text(targetCount);
        }

        // Hide "uncompare" section, show "compare" button
        $wrapper.addClass('hidden');
        $container.find('.js-compare').removeClass('hidden');

        // Unhighlight previously compared row
        $container.parents('.js-table-row').removeClass('highlight');
      });
    });

    $page.on('change', '.js-technique-type', function() {
      updateMeasurementSubjects($(this).parents('form'));
    });

    updateMeasurementSubjects($page.find('.js-calculation-form'));

    function updateMeasurementSubjects($form) {
      let $techniqueSelect = $form.find('.js-technique-type');
      let techniqueId = $techniqueSelect.val();

      $form.find('[data-technique-id]').addClass('hidden')
      $form.find(`[data-technique-id=${techniqueId}]`).removeClass('hidden')
    }

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

    function updateCompareBox(action, target, successCallback) {
      $.ajax({
        type: 'POST',
        url: `/comparison/update/${action}.json`,
        data: JSON.stringify({'target': target}),
        cache: false,
        contentType: 'application/json',
        processData: true,
        success: function(response) {
          successCallback(JSON.parse(response))
        },
      })
    }
  });
});

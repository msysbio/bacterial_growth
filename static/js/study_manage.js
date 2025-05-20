Page('.study-manage-page', function($page) {
  let studyId = $page.data('studyId');
  let $form   = $page.find('.js-modeling-form');

  updateFormVisibility($form);

  $page.find('.js-experiment-container').each(function(e) {
    let $container = $(this);

    if ($container.find('input[type=checkbox]:checked').length > 0) {
      $container.removeClass('hidden');
      return;
    }
  });

  // Activate the preview when checking a new item:
  $page.on('change', 'input.js-measurement-toggle', function(e) {
    let $checkbox = $(e.currentTarget);

    if ($checkbox.is(':checked')) {
      let $row = $checkbox.parents('.js-technique-row');
      $row.find('.js-edit-trigger').trigger('click');
    }
  });

  $page.on('change', 'form.js-modeling-form', function(e) {
    let $form = $(e.currentTarget);
    updateFormVisibility($form);

    let $activeTrigger = $('.js-technique-row.highlight:visible .js-edit-trigger');
    if ($activeTrigger.length > 0) {
      updateChart($activeTrigger.first());
    }
  });

  $page.on('click', '.js-select-all', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox].js-measurement-toggle:visible').prop('checked', true);

    updateFormVisibility($form)
  });

  $page.on('click', '.js-clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox]').prop('checked', false);

    updateFormVisibility($form)
  });

  $page.on('click', '.js-edit-trigger', function(e) {
    e.preventDefault();

    let $trigger = $(this);
    updateChart($trigger)
  });

  $page.on('submit', '.js-modeling-form', function(e) {
    e.preventDefault();
    let $form = $(e.currentTarget);

    $.ajax({
      url: $form.attr('action'),
      dataType: 'json',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        let modelingRequestId = response.modelingRequestId;
        let $result = $page.find('.js-calculation-result');

        function check() {
          $.ajax({
            url: `/study/${studyId}/modeling/check.json`,
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

              let $activeTrigger = $('.js-technique-row.highlight:visible .js-edit-trigger');
              if ($activeTrigger.length > 0) {
                updateChart($activeTrigger.first());
              }
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

  // TODO: duplicates study_visualize.js, except for the form submission
  function updateFormVisibility($form) {
    let selectedExperimentId = $form.find('select[name="experimentId"]:visible').val();

    $form.find('.js-experiment-container').addClass('hidden');
    $form.find('.js-technique-row').addClass('hidden');

    let $experiment = $form.find(`.js-experiment-container[data-experiment-id="${selectedExperimentId}"]`);
    $experiment.removeClass('hidden');

    let selectedTechniqueId = $experiment.
      find('select[name="techniqueId"]').val();
    let selectedTechniqueSubjectType = $experiment.
      find('select[name="techniqueId"] option:selected').data('subjectType');

    $experiment.
      find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"]`).
      removeClass('hidden');
  }

  function updateChart($trigger) {
    let $form = $trigger.parents('form');
    let url   = $trigger.attr('href');

    let $chart       = $form.find('.js-chart');
    let modelingType = $form.find('select[name=modelingType]').val();
    let logTransform = $form.find('input[name=logTransform]').prop('checked');

    $page.find('.js-technique-row').removeClass('highlight');
    $trigger.parents('.js-technique-row').addClass('highlight');

    $.ajax({
      url: url,
      dataType: 'html',
      data: {
        'modelingType': modelingType,
        'logTransform': logTransform,
        'width':        $chart.width(),
        'height':       $chart.height(),
      },
      success: function(response) {
        $chart.html(response)
      },
    });
  }
});

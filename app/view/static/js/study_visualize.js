Page('.study-visualize-page', function($page) {
  let $compareData = $(document).find('[data-compare-ids]')

  let studyId = $page.data('studyId')
  let $form   = $page.find('.js-chart-form');

  updateChart($form).then(function() {
    let checkboxesChanged = false;

    // For each row in the preview form, check if it should be initialized on
    // the left or right:
    $form.find('.js-contexts-list .js-row').each(function() {
      let $chartRow = $(this);
      let contextId = $chartRow.data('contextId');
      let $formRow = $form.find(`input[name="measurementContext|${contextId}"]`);

      if (($formRow).is('[data-axis-right]')) {
        $chartRow.find('.js-axis-left').prop('checked', false);
        $chartRow.find('.js-axis-right').prop('checked', true);
        checkboxesChanged = true;
      }
    });

    if (checkboxesChanged) {
      updateChart($form);
    }
  });

  $page.find('.js-experiment-container').each(function(e) {
    let $container = $(this);

    if ($container.find('input[type=checkbox]:checked').length > 0) {
      $container.removeClass('hidden');
      return;
    }
  });

  // Exclusive checkboxes on one row:
  $page.on('change', 'input.js-axis', function(e) {
    let $checkbox = $(e.currentTarget);
    let $other;

    if ($checkbox.is('.js-axis-left')) {
      $other = $checkbox.parents('.js-row').find('.js-axis-right');
    } else if ($checkbox.is('.js-axis-right')) {
      $other = $checkbox.parents('.js-row').find('.js-axis-left');
    }

    if ($checkbox.is(':checked')) {
      $other.prop('checked', false);
    } else {
      $other.prop('checked', true);
    }
  });

  $page.on('change', 'form.js-chart-form', function(e) {
    let $form = $(e.currentTarget);
    updateChart($form);
  });

  $page.on('click', '.js-select-all', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox].js-measurement-toggle:visible').prop('checked', true);

    updateChart($form)
  });

  $page.on('click', '.js-clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox]').prop('checked', false);

    updateChart($form)
  });

  $page.on('click', '.js-compare', function(e) {
    e.preventDefault();

    let contextIds = [];
    $('.js-contexts-list [data-context-id]').each(function() {
      contextIds.push($(this).data('contextId'));
    });

    updateCompareData('add', contextIds);
  });

  function updateChart($form) {
    let selectedExperimentId = $form.find('select[name="experimentId"]').val();

    $form.find('.js-experiment-container').addClass('hidden');
    $form.find('.js-technique-row').addClass('hidden');

    let $experiment = $form.find(`.js-experiment-container[data-experiment-id="${selectedExperimentId}"]`);
    $experiment.removeClass('hidden');

    let selectedTechniqueId = $form.
      find('select[name="techniqueId"]').val();
    let selectedTechniqueSubjectType = $form.
      find('select[name="techniqueId"] option:selected').data('subjectType');

    $experiment.
      find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"]`).
      removeClass('hidden');

    // Update chart:

    let $chart = $form.find('.chart');

    let width          = Math.floor($chart.width());
    let scrollPosition = $(document).scrollTop();

    return $.ajax({
      url: `/study/${studyId}/visualize/chart?width=${width}`,
      dataType: 'html',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        $chart.html(response);
        $(document).scrollTop(scrollPosition);
      }
    })
  }

  // TODO duplicates study.js, extract
  function updateCompareData(action, contexts, successCallback) {
    $.ajax({
      type: 'POST',
      url: `/comparison/update/${action}.json`,
      data: JSON.stringify({'contexts': contexts}),
      cache: false,
      contentType: 'application/json',
      processData: true,
      success: function(response) {
        let compareData = JSON.parse(response);

        let countText;
        if (compareData.contextCount > 0) {
          countText = `(${compareData.contextCount})`;
        } else {
          countText = '';
        }

        let $sidebarCompareItem = $(document).find('.js-sidebar-compare');
        $sidebarCompareItem.find('.js-count').html(countText);

        $sidebarCompareItem.addClass('highlight');
        setTimeout(function() {
          $sidebarCompareItem.removeClass('highlight');
        }, 500);

        if (successCallback) {
          successCallback(compareData);
        }
      },
    })
  }
});

Page('.study-visualize-page', function($page) {
  let studyId = $page.data('studyId')
  let $form   = $page.find('.js-chart-form');

  update_chart($form);

  $page.find('.js-experiment-container').each(function(e) {
    let $container = $(this);

    if ($container.find('input[type=checkbox]:checked').length > 0) {
      $container.removeClass('hidden');
      return;
    }
  });

  $(document).on('x-sidebar-resize', function() {
    $('.js-plotly-plot').each(function() {
      let $chart = $(this);
      let width = Math.floor($chart.parents('.chart').width());

      Plotly.relayout($chart[0], { 'width': width }, 0);
    });
  });

  $page.on('change', 'form.js-chart-form', function(e) {
    let $form = $(e.currentTarget);
    update_chart($form);
  });

  $page.on('click', '.clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $container = $link.parents('.js-experiment-container');
    $container.find('input[type=checkbox]').prop('checked', false);

    update_chart($container.find('form'))
  });

  function update_chart($form) {
    let selectedExperimentId = $form.find('select[name="experimentId"]:visible').val();

    $form.find('.js-experiment-container').addClass('hidden');
    $form.find(`.js-experiment-container[data-experiment-id="${selectedExperimentId}"]`).removeClass('hidden');

    let selectedTechniqueId          = $form.find('select[name="techniqueId"]:visible').val();
    let selectedTechniqueSubjectType = $form.find('select[name="techniqueId"]:visible option:selected').data('subjectType');

    $form.find('.js-technique-row').addClass('hidden');

    if (selectedTechniqueSubjectType == 'bioreplicate') {
      // Hide bioreplicate select box, show all checkboxes (with bioreplicates)
      $form.find('select[name="bioreplicateId"]').addClass('hidden');
      $form.
        find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"]`).
        removeClass('hidden');
    } else {
      // Show bioreplicate select box, show all checkboxes (with bioreplicates)
      $form.find('select[name="bioreplicateId"]').removeClass('hidden');

      let selectedBioreplicateId = $form.find('select[name="bioreplicateId"]:visible').val();

      $form.
        find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"][data-bioreplicate-id="${selectedBioreplicateId}"]`).
        removeClass('hidden');
    }

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

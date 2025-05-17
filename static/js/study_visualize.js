Page('.study-visualize-page', function($page) {
  let studyId = $page.data('studyId')
  let $form   = $page.find('.js-chart-form');

  update_chart($form);

  $('.js-chart-form [name=experimentId]').select2({
    theme: 'custom',
    width: '100%',
  });
  $('.js-chart-form [name=techniqueId]').select2({
    theme: 'custom',
    width: '100%',
  });
  $('.js-chart-form [name=bioreplicateCompartmentId]').select2({
    theme: 'custom',
    width: '100%',
  });

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
    update_chart($form);
  });

  $page.on('click', '.js-clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('input[type=checkbox]').prop('checked', false);

    update_chart($form)
  });

  function update_chart($form) {
    let selectedExperimentId = $form.find('select[name="experimentId"]:visible').val();

    $form.find('.js-experiment-container').addClass('hidden');
    $form.find(`.js-experiment-container[data-experiment-id="${selectedExperimentId}"]`).removeClass('hidden');

    let selectedTechniqueId = $form.
      find('select[name="techniqueId"]:visible').val();
    let selectedTechniqueSubjectType = $form.
      find('select[name="techniqueId"]:visible option:selected').data('subjectType');

    $form.find('.js-technique-row').addClass('hidden');

    if (selectedTechniqueSubjectType == 'bioreplicate') {
      // Hide bioreplicate select box, show all checkboxes (with bioreplicates)
      $form.find('.js-bioreplicate-row').addClass('hidden');
      $form.
        find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"]`).
        removeClass('hidden');
    } else {
      // Show bioreplicate select box, show all checkboxes (with bioreplicates)
      $form.find('.js-bioreplicate-row').removeClass('hidden');

      let selectedBioreplicateCompartmentId = $form.
        find('select[name="bioreplicateCompartmentId"]:visible').val();
      let [bioreplicateId, compartmentId] = selectedBioreplicateCompartmentId.split('|');

      let selector1 = `[data-technique-id="${selectedTechniqueId}"]`;
      let selector2 = `[data-bioreplicate-id="${bioreplicateId}"]`;
      let selector3 = `[data-compartment-id="${compartmentId}"]`;

      $form.find(`.js-technique-row${selector1}${selector2}${selector3}`).removeClass('hidden');
    }

    let $chart = $form.find('.chart');

    let width          = Math.floor($chart.width());
    let scrollPosition = $(document).scrollTop();

    $.ajax({
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
});

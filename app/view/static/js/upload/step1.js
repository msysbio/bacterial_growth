Page('.upload-page .step-content.step-1.active', function($step1) {
  let $form = $step1.find('form');

  updateProjectFields();
  updateStudyFields();

  $step1.on('change', '.js-project-select', function() { updateProjectFields(); });
  $step1.on('change', '.js-study-select', function() { updateStudyFields(); });

  function updateProjectFields() {
    let $select = $form.find('.js-project-select');
    let $option = $select.find('option:selected');

    let $name = $form.find('input[name=project_name]');
    if ($name.val() == '') {
      $name.val($option.data('name'));
    }
    let $description = $form.find('textarea[name=project_description]');
    if ($description.val() == '') {
      $description.val($option.data('description'));
    }

    // If the selected study is not in this project, reset the study form
    if ($option.val() != '_new') {
      let selectedStudyUuid = $form.find('.js-study-select option:selected').val();
      let projectStudies = $option.data('studyUuids');

      if (!projectStudies.includes(selectedStudyUuid)) {
        $form.find('.js-study-select').val('_new').trigger('change');
      }
    }
  }

  function updateStudyFields() {
    let $select = $form.find('.js-study-select');
    let $option = $select.find('option:selected');

    $form.find('input[name=study_name]').val($option.data('name'));
    $form.find('textarea[name=study_description]').val($option.data('description'));

    // If the selected project is not the parent of this study, find it in the project form
    if ($option.val() != '_new') {
      let selectedProjectUuid = $form.find('.js-project-select option:selected').val();
      let projectUuid = $option.data('projectUuid');

      if (projectUuid != selectedProjectUuid) {
        $form.find('.js-project-select').val(projectUuid).trigger('change');
      }
    }
  }
});

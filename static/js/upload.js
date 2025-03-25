$(document).ready(function() {
  $('.upload-page .step-content.step-1.active').each(function() {
    let $step1 = $(this);
    let $form = $step1.find('form');

    updateProjectFields();
    updateStudyFields();

    $step1.on('change', '.js-project-select', function() { updateProjectFields(); });
    $step1.on('change', '.js-study-select', function() { updateStudyFields(); });

    function updateProjectFields() {
      let $select = $form.find('.js-project-select');
      let $option = $select.find('option:selected');

      $form.find('input[name=project_name]').val($option.data('name'));
      $form.find('textarea[name=project_description]').val($option.data('description'));

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

  $('.upload-page .step-content.step-2.active').each(function() {
    let $step2 = $(this);

    $step2.on('click', '.js-add-strain', function(e) {
      e.preventDefault();
      addNewStrainForm($(e.currentTarget), {});
    });

    $step2.on('click', '.js-remove-new-strain', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-new-strain-container').remove();
    });

    let $multipleStrainSelect = $step2.find('.js-multiple-strain-select');

    $multipleStrainSelect.select2({
      multiple: true,
      width: '100%',
      theme: 'custom',
      minimumInputLength: 1,
      ajax: {
        url: '/strains/completion',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter,
    });

    $multipleStrainSelect.on('change', function() {
      let $form       = $multipleStrainSelect.parents('form');
      let $strainList = $form.find('.strain-list');
      let template    = $form.find('template.strain-list-item').html();
      let selectedIds = new Set($multipleStrainSelect.val());

      $strainList.html('');

      $(this).find('option').each(function() {
        let $option = $(this);
        let name    = $option.text().replace(/\s*\(NCBI:.*\)/, '');
        let id      = $option.val();

        if (!selectedIds.has(id)) {
          return;
        }

        let newListItemHtml = template.
          replaceAll('${id}', id).
          replaceAll('${name}', name);

        $strainList.append($(newListItemHtml));
      });
    });

    $multipleStrainSelect.trigger('change');

    function addNewStrainForm($addStrainButton, newStrain) {
      // We need to prepend all names and ids with "new-strain-N" for uniqueness:

      let newStrainIndex = $step2.find('.js-new-strain-container').length;
      let templateHtml = $step2.find('template.new-strain').html();
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('input[name=name]').
        attr('name', `new_strains-${newStrainIndex}-name`);
      $newForm.find('textarea[name=description]').
        attr('name', `new_strains-${newStrainIndex}-description`);
      $newForm.find('select[name=species]').
        attr('name', `new_strains-${newStrainIndex}-species`);

      // Insert into DOM
      $addStrainButton.parents('.form-row').before($newForm);

      // Initialize single-strain selection:
      let $strainSelect = $newForm.find('.js-single-strain-select');
      initializeSingleStrainSelect($strainSelect);
    }

    function initializeSingleStrainSelect($select) {
      $select.select2({
        placeholder: 'Select parent species',
        theme: 'custom',
        width: '100%',
        minimumInputLength: 1,
        ajax: {
          url: '/strains/completion',
          dataType: 'json',
          delay: 100,
          cache: true,
        },
        templateResult: select2Highlighter,
      });

      $select.on('change', function() { updateParentPreview($select) });

      function updateParentPreview($select) {
        let $container     = $select.parents('.js-new-strain-container').log();
        let $parentPreview = $container.find('.js-parent-preview').log();
        let template       = $('template.new-strain-parent-preview').html();
        let selectedId     = $select.val();

        $parentPreview.html('');

        $select.find('option').each(function() {
          let $option = $(this);
          let name    = $option.text().replace(/\s*\(NCBI:.*\)/, '');
          let id      = $option.val();

          if (selectedId != id) {
            return;
          }

          let previewHtml = template.
            replaceAll('${id}', id).
            replaceAll('${name}', name);

          $parentPreview.append($(previewHtml));
        });
      }

      updateParentPreview($select);
    };

    $step2.find('.js-single-strain-select').each(function() {
      initializeSingleStrainSelect($(this));
    });
  });

  $('.upload-page .step-content.step-3.active').each(function() {
    let $step3     = $(this);
    let $step3form = $step3.find('form');

    $('select[name=vessel_type]').on('change', function() {
      updateVesselCountInputs();
    });

    updateVesselCountInputs();

    function updateVesselCountInputs() {
      let $vesselTypeInput = $step3form.find('select[name=vessel_type]');
      let vesselType = $vesselTypeInput.val();

      $step3form.find('.vessel-count').addClass('hidden');
      $step3form.find(`.vessel-${vesselType}`).removeClass('hidden');
    }

    $('select#technique_types').select2({
      theme: 'custom',
    });

    let $metabolitesSelect = $('.js-metabolites-select');

    $metabolitesSelect.select2({
      multiple: true,
      theme: 'custom',
      width: '100%',
      minimumInputLength: 1,
      ajax: {
        url: '/metabolites/completion',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter,
    });
    $metabolitesSelect.trigger('change');
  });

  $('.upload-page .step-content.step-4.active').each(function() {
    let $step4 = $(this);

    $step4.on('dragover', '.js-file-upload', function(e) {
      e.preventDefault();
      $(this).addClass('drop-hover');
    });
    $step4.on('dragleave', '.js-file-upload', function(e) {
      e.preventDefault();
      $(this).removeClass('drop-hover');
    });
    $step4.on('drop', '.js-file-upload', function(e) {
      e.preventDefault();

      let $container = $(this).parents('.js-upload-container');
      let $input = $container.find('input[type=file]')
      $input[0].files = e.originalEvent.dataTransfer.files;

      $(this).removeClass('drop-hover');
      submitExcelForm($container);
    });
    $step4.on('change', 'input[type=file]', function(e) {
      let $container = $(this).parents('.js-upload-container');
      submitExcelForm($container);
    });

    $step4.on('change', '.js-preview select', function() {
      let $select       = $(this);
      let selectedSheet = $select.val();

      $sheets = $(this).parents('.js-preview').find('.js-sheet');
      $sheets.addClass('hidden');

      if (selectedSheet != '') {
        $sheets.filter(`.js-sheet-${selectedSheet}`).removeClass('hidden');
      }
    });

    // Trigger initial sheet preview
    $('.js-preview select').trigger('change');

    function submitExcelForm($container) {
      let url        = $container.prop('action')
      let $preview   = $container.find('.js-preview');
      let $fileInput = $container.find('input[type=file]');
      let formData   = new FormData();
      let file       = $fileInput[0].files[0];

      formData.append("file", file, file.name);

      $.ajax({
        type: 'POST',
        url: '/upload/spreadsheet_preview',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(response) {
          $preview.html(response);
          $preview.find('select').trigger('change');
        }
      })
    }
  });
});

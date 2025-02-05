$(document).ready(function() {
  $('.upload-page .step-content.step-1').each(function() {
    let $step1 = $(this);

    // Show form corresponding to currently selected submission type
    showForms($step1.find('.js-submission-type').val());

    // Show form when submission type changes
    $step1.on('change', '.js-submission-type', function() {
      let $select        = $(this);
      let submissionType = $select.val();

      showForms(submissionType);
    });

    function showForms(submissionType) {
      $forms = $step1.find('.submission-forms form');
      $forms.addClass('hidden');

      if (submissionType != '') {
        $forms.filter(`#form-${submissionType}`).removeClass('hidden');
      }
    }
  });

  $('.upload-page .step-content.step-2').each(function() {
    let $step2 = $(this);

    $step2.on('click', '.js-add-strain', function(e) {
      e.preventDefault();
      add_new_strain_form($(e.currentTarget), {});
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
      ajax: {
        url: '/strains/completion',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter($multipleStrainSelect),
    });

    $multipleStrainSelect.on('change', function() {
      let $form       = $multipleStrainSelect.parents('form');
      let $strainList = $form.find('.strain-list');
      let template    = $form.find('template.strain-list-item').html();
      let selectedIds = new Set($multipleStrainSelect.val());

      $strainList.html('');

      $(this).find('option').each(function() {
        let $option = $(this);
        let name    = $option.text();
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

    function add_new_strain_form($addStrainButton, newStrain) {
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
      initialize_single_strain_select($strainSelect);
    }

    function initialize_single_strain_select($select) {
      $select.select2({
        placeholder: 'Select parent species',
        theme: 'custom',
        width: '100%',
        ajax: {
          url: '/strains/completion',
          dataType: 'json',
          delay: 100,
          cache: true,
        },
      });
    }

    initialize_single_strain_select($step2.find('.js-single-strain-select'));

    function update_strain_list() {
      let $form       = $multipleStrainSelect.parents('form');
      let $strainList = $form.find('.strain-list');
      let template    = $form.find('template.strain-list-item').html();
      let selectedIds = new Set($multipleStrainSelect.val());

      $strainList.html('');

      $(this).find('option').each(function() {
        let $option = $(this);
        let name    = $option.text();
        let id      = $option.val();

        if (!selectedIds.has(id)) {
          return;
        }

        let newListItemHtml = template.
          replaceAll('${id}', id).
          replaceAll('${name}', name);

        $strainList.append($(newListItemHtml));
      });
    }
  });

  $('.upload-page .step-content.step-3').each(function() {
    let $step3     = $(this);
    let $step3form = $step3.find('form');

    $('select[name=vessel_type]').on('change', function() {
      update_vessel_count_inputs();
    });

    update_vessel_count_inputs();

    function update_vessel_count_inputs() {
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
      ajax: {
        url: '/metabolites/completion',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter($metabolitesSelect),
    });
    $metabolitesSelect.trigger('change');
  });

  $('.upload-page .step-content.step-4').each(function() {
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
      submit_excel_form($container);
    });
    $step4.on('change', 'input[type=file]', function(e) {
      let $container = $(this).parents('.js-upload-container');
      submit_excel_form($container);
    });

    function submit_excel_form($container) {
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

          $preview.find('select').on('change', function() {
            let $select       = $(this);
            let selectedSheet = $select.val();

            // TODO reusable util
            $sheets = $preview.find('.js-sheet');
            $sheets.addClass('hidden');

            if (selectedSheet != '') {
              $sheets.filter(`.js-sheet-${selectedSheet}`).removeClass('hidden');
            }
          });

          $preview.find('select').trigger('change');
        }
      })
    }
  });
});

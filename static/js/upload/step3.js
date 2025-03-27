$(document).ready(function() {
  $('.upload-page .step-content.step-3.active').each(function() {
    let $step3 = $(this);

    $('select[name=vessel_type]').on('change', function() {
      updateVesselCountInputs();
    });

    updateVesselCountInputs();

    function updateVesselCountInputs() {
      let $vesselTypeInput = $step3.find('select[name=vessel_type]');
      let vesselType = $vesselTypeInput.val();

      $step3.find('.vessel-count').addClass('hidden');
      $step3.find(`.vessel-${vesselType}`).removeClass('hidden');
    }

    $step3.on('click', '.js-add', function(e) {
      e.preventDefault();

      let $addButton = $(e.currentTarget);
      addTechniqueForm($addButton);
    });

    $step3.on('click', '.js-remove', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-technique-container').remove();
    });

    function addTechniqueForm($addButton) {
      let subjectType;
      let templateHtml;

      if ($addButton.is('.js-add-bioreplicate')) {
        subjectType = 'bioreplicate'
        templateHtml = $('template.bioreplicate-form').html();
      } else if ($addButton.is('.js-add-strains')) {
        subjectType = 'strain'
        templateHtml = $('template.strain-form').html();
      } else if ($addButton.is('.js-add-metabolites')) {
        subjectType = 'metabolite'
        templateHtml = $('template.metabolite-form').html();
      }

      let techniqueIndex = $step3.find('.js-technique-container').length;
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('select[name=type]').
        attr('name', `technique-${techniqueIndex}-type`);
      $newForm.find('select[name=units]').
        attr('name', `technique-${techniqueIndex}-units`);
      $newForm.find('textarea[name=description]').
        attr('name', `technique-${techniqueIndex}-description`);

      // Specific types of measurements require specific units:
      $newForm.on('change', '.js-type-select', function() {
        let $typeSelect = $(this);
        updateUnitSelect($newForm, $typeSelect);
      });

      updateUnitSelect($newForm, $newForm.find('.js-type-select'));

      // When the type or unit of measurement change, generate preview:
      $newForm.on('change', '.js-type-select,.js-unit-select', function() {
        updatePreview($newForm, subjectType);
      });

      updatePreview($newForm, subjectType);

      $newForm.find('.js-metabolites-select').each(function() {
        let $select = $(this);

        $select.select2({
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

        $select.trigger('change');
      });

      // Insert into DOM
      $addButton.parents('.form-row').before($newForm);
    }

    function updateUnitSelect($form, $typeSelect) {
      let $unitsSelect = $form.find('.js-unit-select');
      let type = $typeSelect.val();

      if (type == 'ph') {
        $unitsSelect.val('');
        $unitsSelect.prop('disabled', true);
      } else if (type == '16s') {
        $unitsSelect.val('reads');
        $unitsSelect.prop('disabled', true);
      } else {
        $unitsSelect.prop('disabled', false);
      }
    }

    function updatePreview($form, subjectType) {
      let $typeSelect = $form.find('.js-type-select');
      let $unitsSelect = $form.find('.js-unit-select');

      let type = $typeSelect.find('option:selected').data('shortName');
      let units = '(' + $unitsSelect.find('option:selected').text() + ')';
      let subject = null;

      if (subjectType == 'strain') {
        subject = '&lt;strain name&gt;';
        type = null;
      } else if (subjectType == 'metabolite') {
        subject = '&lt;metabolite name&gt;';
        type = null;
      }

      console.log([subject, type, units]);

      if (units == '(N/A)') {
        units = null;
      }

      console.log([subject, type, units].filter(Boolean));

      let columnName = [subject, type, units].filter(Boolean).join(' ');
      let previewText = `Column name in spreadsheet: <strong>${columnName}</strong>`;

      $form.find('.js-preview').html(previewText);
    }
  });
});

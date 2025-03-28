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
      $newForm.find('input,select,textarea').each(function() {
        let $input = $(this);
        let name = $input.attr('name');
        $input.attr('name', `techniques-${techniqueIndex}-${name}`);
      });

      initializeTechniqueForm($newForm);

      // Insert into DOM
      $addButton.parents('.form-row').before($newForm);
    }

    // Initialize existing forms:
    $('.js-technique-container').each(function() {
      let $container = $(this);
      let subjectType = $container.data('subjectType');

      initializeTechniqueForm($(this), subjectType);
    });

    function initializeTechniqueForm($container, subjectType) {
      // Specific types of measurements require specific units:
      $container.on('change', '.js-type-select', function() {
        let $typeSelect = $(this);
        updateUnitSelect($container, $typeSelect);
      });
      updateUnitSelect($container, $container.find('.js-type-select'));

      // When the type or unit of measurement change, generate preview:
      $container.on('change', '.js-type-select,.js-unit-select,.js-include-std', function() {
        updatePreview($container, subjectType);
      });
      updatePreview($container, subjectType);

      // If there is a metabolite dropdown, set up its behaviour
      $container.find('.js-metabolites-select').each(function() {
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
    }

    function updateUnitSelect($container, $typeSelect) {
      let $unitsSelect = $container.find('.js-unit-select');
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

    function updatePreview($container, subjectType) {
      let $typeSelect = $container.find('.js-type-select');
      let $unitsSelect = $container.find('.js-unit-select');
      let $stdCheckbox = $container.find('.js-include-std');

      let type = $typeSelect.find('option:selected').data('shortName');
      let units = '(' + $unitsSelect.find('option:selected').text() + ')';
      let includeStd = $stdCheckbox.is(':checked');
      let subject = null;

      if (subjectType == 'strain') {
        subject = '&lt;strain name&gt;';
      } else if (subjectType == 'metabolite') {
        subject = '&lt;metabolite name&gt;';
        type = null;
      }

      if (units == '(N/A)') {
        units = null;
      }

      let columnName = [subject, type, units].filter(Boolean).join(' ');
      let previewLines = ["Column name(s) in spreadsheet:", "<ul>"]
      previewLines.push(`<li><strong>${columnName}</strong></li>`);

      if (includeStd) {
        let columnName = [subject, type, 'STD'].filter(Boolean).join(' ');
        previewLines.push(`<li><strong>${columnName}</strong></li>`)
      }

      previewLines.push("</ul>");

      $container.find('.js-preview').html(previewLines.join("\n"));
    }

  });
});

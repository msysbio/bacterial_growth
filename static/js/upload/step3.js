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
      let templateHtml;

      if ($addButton.is('.js-add-bioreplicate')) {
        templateHtml = $('template.bioreplicate-form').html();
      } else if ($addButton.is('.js-add-strains')) {
        templateHtml = $('template.strain-form').html();
      } else if ($addButton.is('.js-add-metabolites')) {
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
      $newForm.on('change', 'select.js-type-select', function() {
        let $typeSelect = $(this).log();
        let $unitsSelect = $newForm.find('.js-unit-select');

        let type = $typeSelect.val()

        if (type == 'ph') {
          $unitsSelect.val('');
          $unitsSelect.prop('disabled', true);
        } else if (type == '16s') {
          $unitsSelect.val('reads');
          $unitsSelect.prop('disabled', true);
        } else {
          $unitsSelect.prop('disabled', false);
        }
      });

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
  });
});

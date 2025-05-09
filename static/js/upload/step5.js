Page('.upload-page .step-content.step-5.active', function($step5) {
  $step5.initAjaxSubform({
    prefixRegex:    /experiments-(\d+)-/,
    prefixTemplate: 'experiments-{}-',

    buildSubform: function(experimentIndex) {
      let templateHtml = $('template.experiment-form').html();
      let $newForm = $(templateHtml);

      $newForm.addPrefix(`experiments-${experimentIndex}-`);

      return $newForm;
    },

    initializeSubform: function($experimentForm, experimentIndex) {
      // Initialize compartments:
      let $select = $experimentForm.find('.js-compartment-select');
      $select.select2({
        multiple: true,
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      })
      $select.trigger('change');

      // Initialize bioreplicate subforms:
      $experimentForm.find('.js-bioreplicate-form-row').initClientSideSubform({
        buildSubform: function(bioreplicateIndex) {
          let templateHtml = $experimentForm.find('template.bioreplicate-form').html();
          let $bioreplicateForm = $(templateHtml);

          $bioreplicateForm.addPrefix(`experiments-${experimentIndex}-bioreplicates-${bioreplicateIndex}-`);

          return $bioreplicateForm;
        },

        beforeAdd: function($bioreplicateForm) {
          // Find a previous bioreplicate's name to increment its numeric suffix
          let lastName = $experimentForm.
            find('.js-bioreplicate-subform-list .js-subform-container input[name$="-name"]').
            last().
            val();

          if (!lastName || lastName == '') {
            // Find the experiment name, we can take it and add a numeric suffix
            let experimentName = $experimentForm.
              find('input[name$="-name"]').
              last().
              val();

            if (experimentName && experimentName != '') {
              lastName = `${experimentName}_0`;
            }
          }

          if (!lastName || lastName == '') {
            // No previous name found, leave it blank
            return;
          }

          let newName = lastName.replace(/\d+$/, function(m) {
            return parseInt(m[0], 10) + 1
          });

          if (newName == lastName) {
            newName += '_1';
          }

          $bioreplicateForm.find('input[name$="-name"]').val(newName);
        }
      });

      // Initialize perturbation subforms:
      $experimentForm.find('.js-perturbation-form-row').initClientSideSubform({
        buildSubform: function(perturbationIndex) {
          let templateHtml = $experimentForm.find('template.perturbation-form').html();
          let $perturbationForm = $(templateHtml);

          $perturbationForm.addPrefix(`experiments-${experimentIndex}-perturbations-${perturbationIndex}-`);

          return $perturbationForm;
        },

        initializeSubform: function($perturbationForm) {
          $perturbationForm.find('.js-single-select').select2({
            theme: 'custom',
            width: '100%',
            templateResult: select2Highlighter,
          })
        }
      });
    },
  })

  if ($step5.find('.js-experiment-container').length == 0) {
    // By default, add one form
    $step5.find('.js-add-experiment').trigger('click');
  }
});

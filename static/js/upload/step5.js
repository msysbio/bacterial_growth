$(document).ready(function() {
  $('.upload-page .step-content.step-5.active').each(function() {
    let $step5 = $(this);

    $step5.initAjaxSubform({
      prefixRegex:    /experiments-(\d+)-/,
      prefixTemplate: 'experiments-{}-',

      buildSubform: function(index) {
        let templateHtml = $('template.experiment-form').html();
        let $newForm = $(templateHtml);

        $newForm.addPrefix(`experiments-${index}-`);

        return $newForm;
      },

      initializeSubform: function($subform, index) {
        // Initialize compartments:
        let $select = $subform.find('.js-compartment-select');
        $select.select2({
          multiple: true,
          theme: 'custom',
          width: '100%',
          templateResult: select2Highlighter,
        })
        $select.trigger('change');

        // Accessed by javascript later
        $subform.attr('data-index', index);

        // Initialize bioreplicate forms (nested under experiments):
        $subform.on('click', '.js-add-bioreplicate', function(e) {
          e.preventDefault();

          let $addButton = $(e.currentTarget);
          addBioreplicateForm($addButton);
        });

        function addBioreplicateForm($addButton) {
          let templateHtml = $subform.find('template.bioreplicate-form').html();

          let parentFormIndex = $subform.data('index');
          let $subforms       = $subform.find('.js-bioreplicate-container');
          let subformIndex    = $subforms.length;
          let $newForm        = $(templateHtml);

          $newForm.addPrefix(`experiments-${parentFormIndex}-bioreplicates-${subformIndex}-`);

          // Add sequential number:
          $newForm.find('.js-index').text(`${subformIndex + 1}`)

          // Give it a different style:
          $newForm.addClass('new');

          // Insert into DOM
          $subform.find('.js-new-item-anchor').before($newForm);
        }
      },

      onDuplicate: function($newForm) {
        // Reset name
        $newForm.find('input[name$="name"]').val('');
      },
    })

    if ($step5.find('.js-experiment-container').length == 0) {
      // By default, add one form
      $step5.find('.js-add-experiment').trigger('click');
    }
  });
});

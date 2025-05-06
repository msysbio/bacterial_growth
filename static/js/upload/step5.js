$(document).ready(function() {
  $('.upload-page .step-content.step-5.active').each(function() {
    let $step5 = $(this);

    $step5.initAjaxSubform({
      buildSubform: function(index) {
        let templateHtml = $('template.experiment-form').html();
        let $newForm = $(templateHtml);

        $newForm.prefixInputNames(`experiments-${index}-`);

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

          $newForm.prefixInputNames(`experiments-${parentFormIndex}-bioreplicates-${subformIndex}-`);

          // Add sequential number:
          $newForm.find('.js-index').text(`${subformIndex + 1}`)

          // Give it a different style:
          $newForm.addClass('new');

          // Insert into DOM
          $subform.find('.js-new-item-anchor').before($newForm);
        }
      }
    })

    $step5.on('click', '.js-remove', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-subform-container').first().remove();
    });

    // Experiment forms:
    $step5.on('click', '.js-add-experiment', function(e) {
      e.preventDefault();

      let $addButton = $(e.currentTarget);
      let $form = $addButton.parents('form').first();

      $form.ajaxSubmit({
        success: function(response) {
          let $subformList = $form.find('.js-subform-list');
          $subformList.html(response);

          $subformList.find('.js-subform-container').each(function(index) {
            initializeExperimentForm($(this), index);
          });

          let $errorMessageList = $subformList.find('.error-message-list');
          if ($errorMessageList.length == 0) {
            addExperimentForm($addButton);
          } else {
            $(document).scrollTo($errorMessageList, 150);
          }
        }
      })
    });

    if ($step5.find('.js-experiment-container').length == 0) {
      // By default, add one form
      addExperimentForm($step5.find('.js-add-experiment'));
    }

    // Initialize existing forms:
    $('.js-experiment-container').each(function(index) {
      let $container = $(this);

      initializeExperimentForm($(this), index);
    });

    function addExperimentForm($addButton) {
      let templateHtml = $('template.experiment-form').html();
      let subformIndex = $step5.find('.js-experiment-container').length;
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('input,select,textarea').each(function() {
        let $input = $(this);
        let name = $input.attr('name');
        $input.attr('name', `experiments-${subformIndex}-${name}`);
      });

      // Add sequential number:
      $newForm.find('.js-index').text(`${subformIndex + 1}`);

      // Give it a different style:
      $newForm.addClass('new');

      // Insert into DOM right before the anchor
      $addButton.parents('form').find('.js-experiment-subform-list').append($newForm);

      initializeExperimentForm($newForm, subformIndex);
    }

    function initializeExperimentForm($container, index) {
    }
  });
});

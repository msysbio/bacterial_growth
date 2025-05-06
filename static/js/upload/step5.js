$(document).ready(function() {
  $('.upload-page .step-content.step-5.active').each(function() {
    let $step5 = $(this);

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

          addExperimentForm($addButton);
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

      // Insert into DOM
      $addButton.parents('.form-row').before($newForm);

      initializeExperimentForm($newForm, subformIndex);
    }

    function initializeExperimentForm($container, index) {
      let $select = $container.find('.js-compartment-select');
      $select.select2({
        multiple: true,
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      })
      // $select.trigger('change');

      $container.attr('data-index', index);

      // Initialize bioreplicate forms (nested under experiments):
      $container.on('click', '.js-add-bioreplicate', function(e) {
        e.preventDefault();

        let $addButton = $(e.currentTarget);
        addBioreplicateForm($addButton);
      });

      // if ($container.find('.js-bioreplicate-container').length == 0) {
      //   // By default, add one form
      //   addBioreplicateForm($container.find('.js-add-bioreplicate'));
      // }

      function addBioreplicateForm($addButton) {
        let templateHtml = $container.find('template.bioreplicate-form').html();

        let parentFormIndex = $container.data('index');
        let $subforms = $container.find('.js-bioreplicate-container');
        let subformIndex = $subforms.length;
        let $newForm = $(templateHtml);

        // Modify names:
        $newForm.find('input,select,textarea').each(function() {
          let $input = $(this);
          let name = $input.attr('name');
          $input.attr('name', `experiments-${parentFormIndex}-bioreplicates-${subformIndex}-${name}`);
        });

        // Add sequential number:
        $newForm.find('.js-index').text(`${subformIndex + 1}`)

        // Give it a different style:
        $newForm.addClass('new');

        // Insert into DOM
        $container.find('.js-new-item-anchor').before($newForm);
      }
    }
  });
});

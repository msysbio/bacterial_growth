$(document).ready(function() {
  $('.upload-page .step-content.step-5.active').each(function() {
    let $step5 = $(this);

    $step5.on('click', '.js-add-experiment', function(e) {
      e.preventDefault();

      let $addButton = $(e.currentTarget);
      addExperimentForm($addButton);
    });

    $step5.on('click', '.js-remove', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-experiment-container').remove();
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
      $newForm.find('.js-index').text(`${subformIndex + 1}`)

      // Give it a different style:
      $newForm.addClass('new');

      // Insert into DOM
      $addButton.parents('.form-row').before($newForm);

      initializeExperimentForm($newForm);
    }

    function initializeExperimentForm($container) {
      // Nothing?
    }

  });
});

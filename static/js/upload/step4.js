$(document).ready(function() {
  $('.upload-page .step-content.step-4.active').each(function() {
    let $step4 = $(this);

    $step4.on('click', '.js-add-compartment', function(e) {
      e.preventDefault();

      let $addButton = $(e.currentTarget);
      addCompartmentForm($addButton);
    });

    $step4.on('click', '.js-remove-compartment', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-compartment-container').remove();
    });

    function addCompartmentForm($addButton) {
      let templateHtml = $('template.compartment-form').html();

      let compartmentIndex = $step4.find('.js-compartment-container').length;
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('input,select,textarea').each(function() {
        let $input = $(this);
        let name = $input.attr('name');
        $input.attr('name', `compartments-${compartmentIndex}-${name}`);
      });

      // Add sequential number:
      $newForm.find('.js-index').text(`${compartmentIndex + 1}`)

      // Give it a different style:
      $newForm.addClass('new');

      // Insert into DOM
      $addButton.log().parents('.form-row').log().before($newForm);

      initializeCompartmentForm($newForm);
    }

    // Initialize existing forms:
    $('.js-compartment-container').each(function() {
      let $container = $(this);

      initializeCompartmentForm($(this));
    });

    function initializeCompartmentForm($container) {
      // Nothing?
    }

  });
});

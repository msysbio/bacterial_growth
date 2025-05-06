$(document).ready(function() {
  $('.upload-page .step-content.step-4.active').each(function() {
    let $step4 = $(this);

    $step4.on('click', '.js-add-compartment', function(e) {
      e.preventDefault();

      let $addButton = $(e.currentTarget);
      addCompartmentForm($addButton);
    });

    $step4.on('click', '.js-add-community', function(e) {
      e.preventDefault();

      let $addButton = $(e.currentTarget);
      addCommunityForm($addButton);
    });

    $step4.on('click', '.js-remove', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-compartment-container,.js-community-container').remove();
    });

    $step4.on('click', '.js-duplicate', function(e) {
      e.preventDefault();

      console.log("Duplicate");
    });

    function addCompartmentForm($addButton) {
      let templateHtml = $('template.compartment-form').html();

      let subformIndex = $step4.find('.js-compartment-container').length;
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('input,select,textarea').each(function() {
        let $input = $(this);
        let name = $input.attr('name');
        $input.attr('name', `compartments-${subformIndex}-${name}`);
      });

      // Add sequential number:
      $newForm.find('.js-index').text(`${subformIndex + 1}`)

      // Give it a different style:
      $newForm.addClass('new');

      // Insert into DOM
      $addButton.parents('.form-row').before($newForm);

      initializeCompartmentForm($newForm);
    }

    function addCommunityForm($addButton) {
      let templateHtml = $('template.community-form').html();

      let subformIndex = $step4.find('.js-community-container').length;
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('input,select,textarea').each(function() {
        let $input = $(this);
        let name = $input.attr('name');
        $input.attr('name', `communities-${subformIndex}-${name}`);
      });

      // Add sequential number:
      $newForm.find('.js-index').text(`${subformIndex + 1}`)

      // Give it a different style:
      $newForm.addClass('new');

      // Insert into DOM
      $addButton.parents('.form-row').before($newForm);

      initializeCommunityForm($newForm);
    }

    // Initialize existing forms:
    $('.js-community-container').each(function() {
      let $container = $(this);

      initializeCommunityForm($(this));
    });

    function initializeCompartmentForm($container) {
      // Nothing?
    }

    function initializeCommunityForm($container) {
      let $select = $container.find('.js-strain-select');

      $select.select2({
        multiple: true,
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      });

      $select.trigger('change');
    }

  });
});

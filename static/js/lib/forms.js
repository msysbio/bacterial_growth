// Submit a form with ajax, call as:
//
//  let $form = $(...)
//
//  $form.ajaxSubmit({
//    urlParams: { q: 'query' },
//    success: function(response) { ... },
//    ...
//  })
//
// The `urlParams` value is appended to the form URL as a query. Other
// parameters are provided to $.ajax: https://api.jquery.com/jQuery.ajax/
//
$.fn.ajaxSubmit = function(params) {
  let $form = $(this);

  let urlParams = params.urlParams || {};
  let urlQuery = '';

  if (Object.keys(urlParams).length > 0) {
    urlQuery = '?' + $.param(urlParams)
  }

  if (!$form[0].checkValidity()) {
    $form[0].reportValidity();
    return;
  }

  return $.ajax({
    url: $form.prop('action') + urlQuery,
    dataType: 'html',
    method: 'POST',
    data: $form.serializeArray(),
    ...params
  });
}

// Changes the name of all inputs in the given form to add the given prefix.
//
$.fn.prefixInputNames = function(prefix) {
  let $form = $(this);

  $form.find('input,select,textarea').each(function() {
    let $input = $(this);
    let name = $input.attr('name');
    $input.attr('name', `${prefix}${name}`);
  });
}

// Initializes controls to add subforms to a parent form, while submitting the
// form to validate the data so far.
//
// Selectors:
//
// - .js-add-trigger:       Add button
// - .js-remove-trigger:    Remove button
// - .js-subform-list:      Outer container of forms
// - .js-subform-container: Wrapper of each individual form
// - .error-message-list:   Container with errors coming from the server
//
$.fn.initAjaxSubform = function(params) {
  let $container = $(this);

  params = {
    // Dictionary of additional parameters to be attached to the form URL:
    urlParams: {},

    // Create and return a jquery element for the new form:
    buildSubform: function() {},

    // Run any necessary javascript on the newly-created form:
    initializeSubform: function($subform, index) {},

    ...params
  };

  // Run initialization function on all existing subforms:
  $container.find('.js-subform-list').each(function(index) {
    params.initializeSubform($(this), index);
  });

  $container.on('click', '.js-remove-trigger', function(e) {
    e.preventDefault();
    $(e.currentTarget).parents('.js-subform-container').first().remove();
  });

  $container.on('click', '.js-add-trigger', function(e) {
    e.preventDefault();

    let $addButton = $(e.currentTarget);
    let $form      = $addButton.parents('form');

    $form.ajaxSubmit({
      urlParams: params.urlParams,
      success: function(response) {
        let $subformList = $container.find('.js-subform-list').first();
        $subformList.html(response);

        let $subforms = $subformList.find('.js-subform-container');
        let newSubformIndex = $subforms.length;

        $subforms.each(function(index) {
          params.initializeSubform($(this), index);
        });

        let $errorMessageList = $subformList.find('.error-message-list');
        if ($errorMessageList.length == 0) {
          // Build up new form:
          let $newSubform = params.buildSubform(newSubformIndex);

          // Add sequential number:
          $newSubform.find('.js-index').text(`${newSubformIndex + 1}`);

          // Give it a different style:
          $newSubform.addClass('new');

          // Add it to the end of the list:
          $subformList.append($newSubform);

          // Trigger necessary javascript
          params.initializeSubform($newSubform, $subforms.length);
        } else {
          $(document).scrollTo($errorMessageList, 150);
        }
      }
    })
  });
}

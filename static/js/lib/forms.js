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
$.fn.addPrefix = function(prefix) {
  let $form = $(this);

  $form.find('input,select,textarea').each(function() {
    let $input = $(this);

    let name = $input.attr('name');
    $input.attr('name', `${prefix}${name}`);

    let id = $input.attr('id');
    $input.attr('id', `${prefix}${name}`);
  });
}

// Changes the name of all inputs in the given form: sets the numeric index at
// the end of the regex to the given value.
//
$.fn.replacePrefix = function(prefixRegex, prefixValue) {
  let $form = $(this);

  $form.find('input,select,textarea').each(function() {
    let $input = $(this);

    let name = $input.attr('name');
    let newName = name.replace(prefixRegex, prefixValue)
    $input.attr('name', newName);

    let id = $input.attr('id');
    let newId = name.replace(prefixRegex, prefixValue)
    $input.attr('id', newName);
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

    // Name prefix to match when duplicating
    prefixRegex: null,

    // Name prefix template, {} is replaced with the new index
    prefixTemplate: null,

    // Create and return a jquery element for the new form:
    buildSubform: function() {},

    // Triggered after duplication is performed, useful to reset attributes
    // that should be unique:
    onDuplicate: function($subform) {},

    // Run any necessary javascript on the newly-created form:
    initializeSubform: function($subform, index) {},

    ...params
  };

  // Run initialization function on all existing subforms:
  // - Find only outer subform list
  // - Find its direct "container" children
  //
  $container.find('.js-subform-list').first().children('.js-subform-container').each(function(index) {
    params.initializeSubform($(this), index);
  });

  $container.on('click', '.js-remove-trigger', function(e) {
    e.preventDefault();
    e.stopPropagation();

    $(e.currentTarget).parents('.js-subform-container').first().remove();
  });

  $container.on('click', '.js-duplicate-trigger', function(e) {
    e.preventDefault();
    e.stopPropagation();

    if (!params.prefixRegex) {
      console.error("No `prefixRegex` given, don't know how to rename new form");
      return
    }

    let $duplicateButton = $(e.currentTarget);
    let $form            = $duplicateButton.parents('form');
    let $currentSubform  = $(e.currentTarget).parents('.js-subform-container').first();

    let currentSubformIndex = $currentSubform.parent().children().index($currentSubform[0]);

    $form.ajaxSubmit({
      urlParams: params.urlParams,
      success: function(response) {
        loadResponse(response, function($subformList, subformCount) {
          // We load the subform after it's reloaded from the server, but
          // before javascript changes have been applied to it:
          let $currentSubform = $subformList.find('.js-subform-container').eq(currentSubformIndex);
          let $newSubform     = $currentSubform.clone();

          let currentNameExample = $currentSubform.find('input,textarea,select').first().attr('name');
          let currentPrefixMatch = currentNameExample.match(params.prefixRegex);

          if (!currentPrefixMatch) {
            console.error(`Couldn't match ${currentNamePrefix} against ${currentNameExample}`);
            return
          }

          let prefix      = currentPrefixMatch[0];
          let prefixValue = params.prefixTemplate.replace('{}', subformCount);

          $newSubform.replacePrefix(params.prefixRegex, prefixValue);

          // Apply any post-processing:
          params.onDuplicate($newSubform);

          // Add sequential number:
          $newSubform.find('.js-index').text(`${subformCount + 1}`);

          // Give it a different style:
          $newSubform.addClass('new');

          // Add it to the end of the list:
          $subformList.append($newSubform);

          // Trigger necessary javascript
          params.initializeSubform($newSubform, subformCount);
        });
      }
    });
  });

  $container.on('click', '.js-add-trigger', function(e) {
    e.preventDefault();
    e.stopPropagation();

    let $addButton = $(e.currentTarget);
    let $form      = $addButton.parents('form');

    $form.ajaxSubmit({
      urlParams: params.urlParams,
      success: function(response) {
        loadResponse(response, function($subformList, subformCount) {
          // Build up new form:
          let $newSubform = params.buildSubform(subformCount);

          // Add sequential number:
          $newSubform.find('.js-index').text(`${subformCount + 1}`);

          // Give it a different style:
          $newSubform.addClass('new');

          // Add it to the end of the list:
          $subformList.append($newSubform);

          // Trigger necessary javascript
          params.initializeSubform($newSubform, subformCount);
        });
      }
    })
  });

  // Load the HTML form response and then trigger the callback if the result
  // did not contain validation errors.
  //
  // Implements common code used for both adding and duplicating elements.
  //
  function loadResponse(response, callback) {
    let $subformList = $container.find('.js-subform-list').first();
    $subformList.html(response);

    let $subforms = $subformList.find('.js-subform-container');
    let subformCount = $subforms.length;

    let $errorMessageList = $subformList.find('.error-message-list');
    if ($errorMessageList.length == 0) {
      callback($subformList, subformCount);
    } else {
      $(document).scrollTo($errorMessageList, 150);
    }

    $subforms.each(function(index) {
      params.initializeSubform($(this), index);
    });
  }
}

// Initializes controls to add subforms to a parent form, without making any
// server-side requests. Unlike the ajax-based form, this one is more limited.
//
$.fn.initClientSideSubform = function(params) {
  let $container = $(this);

  params = {
    // Create and return a jquery element for the new form:
    buildSubform: function() {},

    // Triggered after a new form is created, before it's actually added to the
    // DOM, allows adding some placeholder data.
    beforeAdd: function($subform) {},

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
    e.stopPropagation();

    $(e.currentTarget).parents('.js-subform-container').first().remove();
  });

  $container.on('click', '.js-add-trigger', function(e) {
    e.preventDefault();
    e.stopPropagation();

    let $addButton = $(e.currentTarget);
    let $form      = $addButton.parents('form');

    let $subformList = $container.find('.js-subform-list').first();
    let subformCount = $subformList.find('.js-subform-container').length;

    // Build up new form:
    let $newSubform = params.buildSubform(subformCount);

    // Add sequential number:
    $newSubform.find('.js-index').text(`${subformCount + 1}`);

    // Give it a different style:
    $newSubform.addClass('new');

    // Trigger pre-add callback
    params.beforeAdd($newSubform);

    // Add it to the end of the list:
    $subformList.append($newSubform);

    // Trigger necessary javascript
    params.initializeSubform($newSubform, subformCount);
  });
}

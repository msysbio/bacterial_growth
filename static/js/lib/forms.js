// Submit a form with ajax, call as:
//
//  let $form = $(...)
//
//  $form.ajaxSubmit({
//    success: function(response) { ... }
//  })
//
// Parameters are provided to $.ajax: https://api.jquery.com/jQuery.ajax/
//
$.fn.ajaxSubmit = function(params) {
  let $form = $(this);

  if (!$form[0].checkValidity()) {
    $form[0].reportValidity();
    return;
  }

  return $.ajax({
    url: $form.prop('action'),
    dataType: 'html',
    method: 'POST',
    data: $form.serializeArray(),
    ...params
  });
}

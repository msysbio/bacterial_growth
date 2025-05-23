Page('.export-page', function($page) {
  let studyId = $page.data('studyId');

  let $form    = $page.find('form');
  let $preview = $page.find('.js-preview');

  $form.on('change', function() { updatePreview($form); });
  $form.on('keyup', 'input[name=custom_delimiter]', function() { updatePreview($form); });

  updatePreview($form);

  $form.on('focus', 'input[name=custom_delimiter]', function() {
    $form.find('input[name=delimiter][value=custom]').prop('checked', true);
  });

  $form.on('click', '.js-select-all', function() {
    $form.find('.section-experiment input[type=checkbox]').prop('checked', true);
    updatePreview($form);
  });

  $form.on('click', '.js-select-none', function() {
    $form.find('.section-experiment input[type=checkbox]').prop('checked', false);
    updatePreview($form);
  });

  function updatePreview($form) {
    $.ajax({
      url: `/study/${studyId}/export/preview`,
      dataType: 'html',
      data: $form.serializeArray(),
      success: function(response) {
        $preview.html(response);
      }
    })

    $form.find('.js-export-url').val($form.prop('action') + '?' + $form.serialize())
  }
});

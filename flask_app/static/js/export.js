$(document).ready(function() {
  $('.export-page').each(function() {
    let $page   = $(this);
    let studyId = $page.data('studyId');

    let $form    = $page.find('form');
    let $preview = $page.find('.js-preview');

    $form.on('change', function() {
      updatePreview($form);
    });

    updatePreview($form);

    function updatePreview($form) {
      $.ajax({
        url: `/study/${studyId}/export/preview`,
        dataType: 'html',
        data: $form.serializeArray(),
        success: function(response) {
          $preview.html(response);
        }
      })
    }
  });
});

Page('.upload-page .step-content.step-6.active', function($step6) {
  $step6.on('dragover', '.js-file-upload', function(e) {
    e.preventDefault();
    $(this).addClass('drop-hover');
  });
  $step6.on('dragleave', '.js-file-upload', function(e) {
    e.preventDefault();
    $(this).removeClass('drop-hover');
  });
  $step6.on('drop', '.js-file-upload', function(e) {
    e.preventDefault();

    let $container = $step6.find('.js-upload-container');
    let $input = $('#data-template-input');
    $input[0].files = e.originalEvent.dataTransfer.files;

    $(this).removeClass('drop-hover');
    submitExcelForm($container);
  });
  $step6.on('change', 'input[type=file]', function(e) {
    let $container = $step6.find('.js-upload-container');
    submitExcelForm($container);
  });

  $step6.on('change', '.js-preview select', function() {
    let $select       = $(this);
    let selectedSheet = $select.val().replaceAll(' ', '-');

    $sheets = $(this).parents('.js-preview').find('.js-sheet');
    $sheets.addClass('hidden');

    if (selectedSheet != '') {
      $sheets.filter(`.js-sheet-${selectedSheet}`).removeClass('hidden');
    }
  });

  // Trigger initial sheet preview
  $('.js-preview select').trigger('change');

  function submitExcelForm($container) {
    let url        = $container.prop('action')
    let $fileInput = $('#data-template-input');
    let formData   = new FormData();
    let file       = $fileInput[0].files[0];
    let $preview   = $step6.find('.js-preview');

    formData.append("file", file, file.name);
    $preview.addClass('loading');

    $.ajax({
      type: 'POST',
      url: '/upload/spreadsheet_preview',
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      success: function(response) {
        $preview.html(response);
        $preview.removeClass('loading');
        $preview.find('select').trigger('change');
      }
    })
  }
});

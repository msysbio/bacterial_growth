$(document).ready(function() {
  $('.upload-page .step-content.step-4.active').each(function() {
    let $step4 = $(this);

    $step4.on('dragover', '.js-file-upload', function(e) {
      e.preventDefault();
      $(this).addClass('drop-hover');
    });
    $step4.on('dragleave', '.js-file-upload', function(e) {
      e.preventDefault();
      $(this).removeClass('drop-hover');
    });
    $step4.on('drop', '.js-file-upload', function(e) {
      e.preventDefault();

      let $container = $(this).parents('.js-upload-container');
      let $input = $container.find('input[type=file]')
      $input[0].files = e.originalEvent.dataTransfer.files;

      $(this).removeClass('drop-hover');
      submitExcelForm($container);
    });
    $step4.on('change', 'input[type=file]', function(e) {
      let $container = $(this).parents('.js-upload-container');
      submitExcelForm($container);
    });

    $step4.on('change', '.js-preview select', function() {
      let $select       = $(this);
      let selectedSheet = $select.val();

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
      let $preview   = $container.find('.js-preview');
      let $fileInput = $container.find('input[type=file]');
      let formData   = new FormData();
      let file       = $fileInput[0].files[0];

      formData.append("file", file, file.name);

      $.ajax({
        type: 'POST',
        url: '/upload/spreadsheet_preview',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(response) {
          $preview.html(response);
          $preview.find('select').trigger('change');
        }
      })
    }
  });
});

$(document).ready(function() {
  let $page = $('.upload-page');
  let $step1 = $page.find('.step-content.step-1');

  $step1.on('change', '.js-submission-type', function() {
    let $select        = $(this);
    let submissionType = $select.val();

    show_forms(submissionType);
  });

  let $select = $step1.find('.js-submission-type');
  show_forms($select.val());

  $page.find('.js-microbial-strain-select').select2({
    multiple: true,
    width: '100%',
    theme: 'custom',
    ajax: {
      url: '/strains/completion',
      dataType: 'json',
      delay: 100,
      cache: true,
    }
  });

  function show_forms(submissionType) {
    $forms = $step1.find('.submission-forms form');
    $forms.addClass('hidden');

    if (submissionType != '') {
      $forms.filter(`#form-${submissionType}`).removeClass('hidden');
    }
  }
});

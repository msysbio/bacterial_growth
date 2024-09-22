$(document).ready(function() {
  let $page = $('.upload-page');
  let $step1 = $page.find('.step-content.step-1');
  let $step2 = $page.find('.step-content.step-2');

  // Show form corresponding to currently selected submission type
  show_forms($step1.find('.js-submission-type').val());

  // Show form when submission type changes
  $step1.on('change', '.js-submission-type', function() {
    let $select        = $(this);
    let submissionType = $select.val();

    show_forms(submissionType);
  });

  let $multipleStrainSelect = $step2.find('.js-multiple-strain-select');

  $multipleStrainSelect.select2({
    multiple: true,
    width: '100%',
    theme: 'custom',
    ajax: {
      url: '/strains/completion',
      dataType: 'json',
      delay: 100,
      cache: true,
    },
  });

  $multipleStrainSelect.on('change', function() {
    let $form       = $multipleStrainSelect.parents('form');
    let $strainList = $form.find('.strain-list');
    let template    = $form.find('template.strain-list-item').html();
    let selectedIds = new Set($multipleStrainSelect.val());

    $strainList.html('');

    $(this).find('option').each(function() {
      let $option = $(this);
      let name    = $option.text();
      let id      = $option.val();

      if (!selectedIds.has(id)) {
        return;
      }

      let newListItemHtml = template.
        replaceAll('${id}', id).
        replaceAll('${name}', name);

      $strainList.append($(newListItemHtml));
    });
  });

  $step2.on('click', '.js-add-strain', function(e) {
    e.preventDefault();

    $button = $(e.currentTarget);
    let $newStrainForm = $(build_new_strain_form());
    $button.parents('.form-row').before($newStrainForm);

    let $strainSelect = $newStrainForm.find('.js-single-strain-select');
    $strainSelect.select2({
      placeholder: 'Select parent species',
      theme: 'custom',
      width: '100%',
      ajax: {
        url: '/strains/completion',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
    });

  });

  $step2.on('click', '.js-remove-new-strain', function(e) {
    e.preventDefault();

    let $newStrain2 = $(e.currentTarget).parents('.form-row.js-new-strain-row-2').log();
    let $newStrain1 = $newStrain2.prev('.form-row.js-new-strain-row-1').log();

    $newStrain1.remove();
    $newStrain2.remove();
  });

  function show_forms(submissionType) {
    $forms = $step1.find('.submission-forms form');
    $forms.addClass('hidden');

    if (submissionType != '') {
      $forms.filter(`#form-${submissionType}`).removeClass('hidden');
    }
  }

  function build_new_strain_form() {
    // We need to prepend all names and ids with "new-strain-N" for uniqueness:

    let newStrainIndex = $page.find('.form-row.js-new-strain-row-1').length;
    let templateHtml = $page.find('template.new-strain').
      html().
      replaceAll('name="', `name="new-strains-${newStrainIndex}-`);

    return templateHtml;
  }
});

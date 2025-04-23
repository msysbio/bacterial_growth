$(document).ready(function() {
  $('.upload-page .step-content.step-2.active').each(function() {
    let $step2 = $(this);

    $step2.on('click', '.js-add-strain', function(e) {
      e.preventDefault();
      addNewStrainForm($(e.currentTarget), {});
    });

    $step2.on('click', '.js-remove-new-strain', function(e) {
      e.preventDefault();
      $(e.currentTarget).parents('.js-new-strain-container').remove();
    });

    let $multipleStrainSelect = $step2.find('.js-multiple-strain-select');

    $multipleStrainSelect.select2({
      multiple: true,
      width: '100%',
      theme: 'custom',
      minimumInputLength: 1,
      ajax: {
        url: `${BASE_URL}/strains/completion`,
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter,
    });

    $multipleStrainSelect.on('change', function() {
      let $form       = $multipleStrainSelect.parents('form');
      let $strainList = $form.find('.strain-list');
      let template    = $form.find('template.strain-list-item').html();
      let selectedIds = new Set($multipleStrainSelect.val());

      $strainList.html('');

      $(this).find('option').each(function() {
        let $option = $(this);
        let name    = $option.text().replace(/\s*\(NCBI:.*\)/, '');
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

    $multipleStrainSelect.trigger('change');

    function addNewStrainForm($addStrainButton) {
      // We need to prepend all names and ids with "new-strain-N" for uniqueness:

      let newStrainIndex = $step2.find('.js-new-strain-container').length;
      let templateHtml = $step2.find('template.new-strain').html();
      let $newForm = $(templateHtml);

      // Modify names:
      $newForm.find('input,select,textarea').each(function() {
        let $input = $(this);
        let name = $input.attr('name');
        $input.attr('name', `new_strains-${newStrainIndex}-${name}`);
      });

      // Give it a different style:
      $newForm.addClass('new');

      // Insert into DOM
      $addStrainButton.parents('.form-row').before($newForm);

      // Initialize single-strain selection:
      let $strainSelect = $newForm.find('.js-single-strain-select');
      initializeSingleStrainSelect($strainSelect);
    }

    function initializeSingleStrainSelect($select) {
      $select.select2({
        placeholder: 'Select parent species',
        theme: 'custom',
        width: '100%',
        minimumInputLength: 1,
        ajax: {
          url: `${BASE_URL}/strains/completion`,
          dataType: 'json',
          delay: 100,
          cache: true,
        },
        templateResult: select2Highlighter,
      });

      $select.on('change', function() { updateParentPreview($select) });

      function updateParentPreview($select) {
        let $container     = $select.parents('.js-new-strain-container');
        let $parentPreview = $container.find('.js-parent-preview');
        let template       = $('template.new-strain-parent-preview').html();
        let selectedId     = $select.val();

        $parentPreview.html('');

        $select.find('option').each(function() {
          let $option = $(this);
          let name    = $option.text().replace(/\s*\(NCBI:.*\)/, '');
          let id      = $option.val();

          if (selectedId != id) {
            return;
          }

          let previewHtml = template.
            replaceAll('${id}', id).
            replaceAll('${name}', name);

          $parentPreview.append($(previewHtml));
        });
      }

      updateParentPreview($select);
    };

    $step2.find('.js-single-strain-select').each(function() {
      initializeSingleStrainSelect($(this));
    });
  });
});

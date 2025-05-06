$(document).ready(function() {
  $('.upload-page .step-content.step-2.active').each(function() {
    let $step2 = $(this);

    // Initialize selection of existing strains
    let $existingStrainSelect = $step2.find('.js-existing-strain-select');
    $existingStrainSelect.select2({
      existing: true,
      width: '100%',
      theme: 'custom',
      minimumInputLength: 1,
      ajax: {
        url: '/strains/completion/',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
      templateResult: select2Highlighter,
    });

    $existingStrainSelect.on('change', function() {
      let $form       = $existingStrainSelect.parents('form');
      let $strainList = $form.find('.strain-list');
      let template    = $form.find('template.strain-list-item').html();
      let selectedIds = new Set($existingStrainSelect.val());

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

    $existingStrainSelect.trigger('change');

    // Initialize creation of new strains:
    $step2.initAjaxSubform({
      buildSubform: function(index) {
        let templateHtml = $('template.new-strain-form').html();
        let $newForm = $(templateHtml);

        $newForm.prefixInputNames(`new_strains-${index}-`);

        return $newForm;
      },

      initializeSubform: function($subform, index) {
        let $select = $subform.find('.js-single-strain-select');

        $select.select2({
          placeholder: 'Select parent species',
          theme: 'custom',
          width: '100%',
          minimumInputLength: 1,
          ajax: {
            url: '/strains/completion/',
            dataType: 'json',
            delay: 100,
            cache: true,
          },
          templateResult: select2Highlighter,
        });

        $select.on('change', function() { updateNewStrainParentPreview($select) });

        updateNewStrainParentPreview($select);
      }
    })

    function updateNewStrainParentPreview($select) {
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
  });
});

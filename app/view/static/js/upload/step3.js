Page('.upload-page .step-content.step-3.active', function($step3) {
  $step3.initAjaxSubform({
    prefixRegex:    /techniques-(\d+)-/,
    prefixTemplate: 'techniques-{}-',

    buildSubform: function (index, $addButton) {
      let templateHtml;

      if ($addButton.is('.js-add-bioreplicate')) {
        templateHtml = $('template.bioreplicate-form').html();
      } else if ($addButton.is('.js-add-strains')) {
        templateHtml = $('template.strain-form').html();
      } else if ($addButton.is('.js-add-metabolites')) {
        templateHtml = $('template.metabolite-form').html();
      }

      let $newForm = $(templateHtml);
      $newForm.addPrefix(`techniques-${index}-`);

      return $newForm;
    },

    initializeSubform: function($subform) {
      let subjectType = $subform.data('subjectType');

      // Specific types of measurements require specific units:
      $subform.on('change', '.js-type-select', function() {
        let $typeSelect = $(this);
        updateUnitSelect($subform, $typeSelect);
      });
      updateUnitSelect($subform, $subform.find('.js-type-select'));

      // When the type or unit of measurement change, generate preview:
      $subform.on('change', '.js-type-select,.js-unit-select,.js-include-std', function() {
        updatePreview($subform, subjectType);
      });
      updatePreview($subform, subjectType);

      // If there is a metabolite dropdown, set up its behaviour
      $subform.find('.js-metabolites-select').each(function() {
        let $select = $(this);

        $select.select2({
          multiple: true,
          theme: 'custom',
          width: '100%',
          minimumInputLength: 1,
          ajax: {
            url: '/metabolites/completion/',
            dataType: 'json',
            delay: 100,
            cache: true,
          },
          templateResult: select2Highlighter,
        });

        $select.trigger('change');
      });
    },
  });

  function updateUnitSelect($container, $typeSelect) {
    let $unitsSelect = $container.find('.js-unit-select');
    let type = $typeSelect.val();

    if (type == 'ph' || type == 'od') {
      $unitsSelect.val('');
    } else if (type == '16s') {
      $unitsSelect.val('reads');
    } else if (type == 'plates') {
      $unitsSelect.val('CFUs/mL');
    } else {
    }
  }

  function updatePreview($container, subjectType) {
    let $typeSelect = $container.find('.js-type-select');
    let $stdCheckbox = $container.find('.js-include-std');

    let columnName = $typeSelect.find('option:selected').data('columnName');
    let includeStd = $stdCheckbox.is(':checked');
    let subject = null;

    if (subjectType == 'bioreplicate') {
      subject = 'Community';
    } else if (subjectType == 'strain') {
      subject = '&lt;strain name&gt;';
    } else if (subjectType == 'metabolite') {
      subject = '&lt;metabolite name&gt;';
      columnName = null;
    }

    columnName = [subject, columnName].filter(Boolean).join(' ');
    let previewLines = ["Column name(s) in spreadsheet:", "<ul>"]
    previewLines.push(`<li><strong>${columnName}</strong></li>`);

    if (includeStd) {
      let stdColumnName = [columnName, 'STD'].filter(Boolean).join(' ');
      previewLines.push(`<li><strong>${stdColumnName}</strong></li>`)
    }

    previewLines.push("</ul>");

    $container.find('.js-preview').html(previewLines.join("\n"));
  }
});

$(document).ready(function() {
  $('.upload-page .step-content.step-4.active').each(function() {
    let $step4 = $(this);

    $step4.find('.js-compartment-section').initAjaxSubform({
      urlParams: { subform_type: 'compartment' },

      prefixRegex:    /compartments-(\d+)-/,
      prefixTemplate: 'compartments-{}-',

      buildSubform: function (index) {
        let templateHtml = $('template.compartment-form').html();
        let $newForm = $(templateHtml);

        $newForm.addPrefix(`compartments-${index}-`);

        return $newForm;
      },

      onDuplicate: function($newForm) {
        // Reset name
        $newForm.find('input[name$="name"]').val('');
      },
    });

    $step4.find('.js-community-section').initAjaxSubform({
      urlParams: { subform_type: 'community' },

      prefixRegex:    /communities-(\d+)-/,
      prefixTemplate: 'communities-{}-',

      buildSubform: function (index) {
        let templateHtml = $('template.community-form').html();
        let $newForm = $(templateHtml);

        $newForm.addPrefix(`communities-${index}-`);

        return $newForm;
      },

      initializeSubform: function($subform, index) {
        let $select = $subform.find('.js-strain-select');

        $select.select2({
          multiple: true,
          theme: 'custom',
          width: '100%',
          templateResult: select2Highlighter,
        });

        $select.trigger('change');
      },

      onDuplicate: function($newForm) {
        // Reset name
        $newForm.find('input[name$="name"]').val('');
      },
    });
  });
});

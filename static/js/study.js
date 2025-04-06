$(document).ready(function() {
  $('.study-page').each(function() {
    let $page = $(this);
    let $compareBox = $(document).find('.js-compare-box')
    let compareData = $compareBox.data();

    // TODO: a timestamp with a check on update?
    if (compareData.targets) {
      compareData['targets'] = new Set(compareData['targets']);
    } else {
      compareData['targets'] = new Set();
    }

    $page.on('click', '.js-compare a', function(e) {
      e.preventDefault();

      let $button    = $(this);
      let $wrapper   = $button.parents('.js-compare');
      let $container = $button.parents('.js-compare-container');

      let targetIdentifier = $container.data('targetIdentifier');

      compareData['targets'].add(targetIdentifier);
      $compareBox.data(compareData);
      $compareBox.find('.js-target-count').text(compareData['targets'].size);
      $compareBox.removeClass('hidden');

      // Hide "compare" button, show "uncompare" button
      $wrapper.addClass('hidden');
      $container.find('.js-uncompare').removeClass('hidden');

      // Highlight compared row
      $container.parents('.js-table-row').addClass('highlight');

      saveCompareBox(compareData);
    });

    $page.on('click', '.js-uncompare a', function(e) {
      e.preventDefault();

      let $button    = $(this);
      let $wrapper   = $button.parents('.js-uncompare');
      let $container = $button.parents('.js-compare-container');

      let targetIdentifier = $container.data('targetIdentifier');

      compareData['targets'].delete(targetIdentifier);
      $compareBox.data(compareData);

      if (compareData['targets'].size == 0) {
        $compareBox.addClass('hidden');
      } else {
        $compareBox.find('.js-target-count').text(compareData['targets'].size);
      }

      // Hide "uncompare" section, show "compare" button
      $wrapper.addClass('hidden');
      $container.find('.js-compare').removeClass('hidden');

      // Unhighlight previously compared row
      $container.parents('.js-table-row').removeClass('highlight');

      saveCompareBox(compareData);
    });

    function saveCompareBox(data) {
      // TODO ajax request to persist compare box in session
    }
  });
});

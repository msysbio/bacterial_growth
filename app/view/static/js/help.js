Page('.help-page', function($page) {
  let $pageList = $page.find('.js-page-list');
  let $searchInput = $('.js-search-input');

  if ($searchInput.val().length >= 0) {
    updatePage($searchInput);
  }

  $page.on('keyup', '.js-search-input', $.debounce(100, function() {
    let $searchInput = $(this);
    updatePage($searchInput);
  }));

  function updatePage($searchInput) {
    let $form = $searchInput.parents('form');
    $pageList.addClass('loading');

    $form.ajaxSubmit({
      success: function(response) {
        $pageList.html(response);
        $pageList.removeClass('loading');
      }
    });
  }
});

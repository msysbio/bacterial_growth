// Evaluates code only on a page defined by the given selector.
//
// If the selector is not specific enough and more than one container matches,
// an error is shown.
//
// The callback is invoked with a jQuery object wrapping the selected
// container.
//
function Page(selector, callback) {
  $(document).ready(function() {
    let $container = $(selector);

    if ($container.length > 1) {
      console.error("Page selector matched more than one element:", $container);
      return;
    }

    callback($container);
  });
}

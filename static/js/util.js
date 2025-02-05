$.fn.log = function() {
  console.log($(this));
  return this;
}

function wrapSubstrings(text, words, prefix, suffix) {
  if (words.length <= 0 || words[0].length <= 0) {
    return text;
  }

  let result         = "";
  let lowercaseText  = text.toLowerCase();
  let lowercaseWords = words.map((s) => s.toLowerCase());

  let currentWordIndex = 0;
  let query            = lowercaseWords[currentWordIndex];

  let previousTextIndex = 0
  let currentTextIndex  = lowercaseText.indexOf(query);

  if (currentTextIndex < 0) {
    return text;
  }

  while (currentTextIndex >= 0 && currentWordIndex < lowercaseWords.length) {
    result += text.substring(previousTextIndex, currentTextIndex);
    result += prefix + text.substring(currentTextIndex, currentTextIndex + query.length) + suffix;

    previousTextIndex = currentTextIndex + query.length;

    currentWordIndex += 1;
    query = lowercaseWords[currentWordIndex];

    currentTextIndex  = lowercaseText.indexOf(query, previousTextIndex + 1);
  }

  result += text.substring(previousTextIndex);

  return result;
}

function select2Highlighter($container) {
  let $searchField;

  // The search field is only available once the dropdown is rendered, so we
  // set it in the immediate next event loop:
  setTimeout(function() {
    $searchField = $container.next('.select2-container').find('.select2-search__field');
  }, 1);

  return function(state) {
    let query = $.trim($searchField.val());
    let text = wrapSubstrings(
      state.text,
      query.split(/\s+/),
      '<span class="select2-highlight">',
      '</span>',
    );

    return $('<div>' + text + '</div>');
  };
}

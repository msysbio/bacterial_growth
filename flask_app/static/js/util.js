$.fn.log = function() {
  console.log($(this));
  return this;
}

function wrapSubstring(text, query, prefix, suffix) {
  if (query.length <= 0) {
    return text;
  }

  let result         = "";
  let lowercaseText  = text.toLowerCase();
  let lowercaseQuery = query.toLowerCase();

  let previousIndex = 0
  let currentIndex  = lowercaseText.indexOf(lowercaseQuery);

  if (currentIndex.length < 0) {
    return text;
  }

  while (currentIndex >= 0) {
    result += text.substring(previousIndex, currentIndex);
    result += prefix + text.substring(currentIndex, currentIndex + query.length) + suffix;

    previousIndex = currentIndex + query.length;
    currentIndex  = lowercaseText.indexOf(lowercaseQuery, previousIndex + 1);
  }

  result += text.substring(previousIndex);

  return result;
}

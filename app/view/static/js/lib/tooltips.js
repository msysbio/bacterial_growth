// Initialize tippy popups:
function initTooltips() {
  tippy('[data-tooltip]', {
    content: function(element) {
      return element.getAttribute('data-tooltip');
    }
  })
}

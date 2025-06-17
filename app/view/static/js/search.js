Page('.search-page', function($page) {
  // Make sure the "advanced search" checkbox reflects the current state of the
  // form:
  let $checkbox = $page.find('#advanced-search-input');
  let $inputs = $checkbox.parents('.form-row').nextAll('.form-row.clause');
  if ($inputs.length == 0) {
    $checkbox.prop('checked', false);
  } else {
    $checkbox.prop('checked', true);
  }

  $page.on('change', '#advanced-search-input', function(e) {
    let checkbox = $(e.currentTarget);

    if (checkbox.is(':checked')) {
      add_advanced_search();
    } else {
      remove_advanced_search();
    }
  });

  $page.on('click', '.js-remove-clause', function(e) {
    e.preventDefault();

    $clause = $(e.currentTarget).parents('.form-row.clause');
    $clause.remove();
  });

  $page.on('click', '.js-add-clause', function(e) {
    e.preventDefault();

    $button = $(e.currentTarget);
    let new_clause = build_new_clause();
    $button.parents('.form-row').before(new_clause);
  });

  function remove_advanced_search() {
    // We find the checkbox and remove all form rows after it:
    let $checkbox = $page.find('#advanced-search-input');
    let $inputs = $checkbox.parents('.form-row').nextAll('.form-row.clause');

    $inputs.remove();

    // We also remove the "Add new" button
    $page.find('.add-clause').parents('.form-row').remove();
  }

  function add_advanced_search() {
    // We find the checkbox and add a single clause afterwards:
    let $checkbox = $page.find('#advanced-search-input');
    let new_clause = build_new_clause();

    $checkbox.parents('.form-row').after(`
      <div class="form-row">
        <a href="#" class="green-button add-clause">Add clause</a>
      </div>
    `);
    $checkbox.parents('.form-row').after(new_clause);
  }

  function build_new_clause() {
    let template_clause = $page.find('#form-clause-template').html();

    // We need to prepend all names and ids with "clause-N" for uniqueness:
    let clause_index = $page.find('.form-row.clause').length;
    template_clause = template_clause.replaceAll('name="', `name="clauses-${clause_index}-`);
    template_clause = template_clause.replaceAll('id="', `id="clauses-${clause_index}-`);

    return template_clause;
  }
});

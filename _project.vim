runtime! projects/flask.vim

silent AckIgnore .micromamba/ flask_app/static/build/ flask_app/static/js/vendor/
silent TagsExclude .micromamba/* flask_app/static/build/* flask_app/static/js/vendor/*

set tags+=micromamba.tags

let bacterial_growth_db_roots = ['.', 'flask_app']

call bacterial_growth_db#Init()

nnoremap ,t :tabnew _project.vim<cr>

runtime! projects/flask.vim

silent AckIgnore .micromamba/ flask_app/static/build/ flask_app/static/js/vendor/
silent TagsExclude .micromamba/* flask_app/static/build/* flask_app/static/js/vendor/*

set tags+=micromamba.tags

let vim_bacterial_growth_roots = ['.', 'flask_app']

call vim_bacterial_growth#Init()

nnoremap ,t :tabnew _project.vim<cr>

command! Eroutes :e flask_app/initialization/routes.py
command! Eschema :e src/sql_scripts/create_db.sql

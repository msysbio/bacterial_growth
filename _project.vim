runtime! projects/flask.vim

silent AckIgnore .micromamba/ static/build/ static/js/vendor/
silent TagsExclude .micromamba/* static/build/* static/js/vendor/*

set tags+=micromamba.tags

let vim_bacterial_growth_roots = ['.']

call vim_bacterial_growth#Init()

nnoremap ,t :tabnew _project.vim<cr>

command! Eroutes :e initialization/routes.py
command! Eschema :e schema.sql

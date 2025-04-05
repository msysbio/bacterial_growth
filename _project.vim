runtime! projects/flask.vim

silent AckIgnore .micromamba/ static/build/ static/js/vendor/ docs/ streamlit
silent TagsExclude .micromamba/* static/build/* static/js/vendor/* docs/* streamlit/*

set tags+=micromamba.tags

let vim_bacterial_growth_roots = ['.']

call vim_bacterial_growth#Init()

nnoremap ,t :tabnew _project.vim<cr>

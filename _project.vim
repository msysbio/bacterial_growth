runtime! projects/flask.vim

silent AckIgnore .micromamba/ static/build/ static/js/vendor/ docs/_build
silent TagsExclude .micromamba/* static/build/* static/js/vendor/* docs/_build/*

set tags+=micromamba.tags

let vim_bacterial_growth_roots = ['.']

call vim_bacterial_growth#Init()

nnoremap ,t :tabnew _project.vim<cr>

command! Eroutes :e initialization/routes.py
command! Eschema :e db/schema.sql

command! -nargs=? -complete=custom,s:CompleteSchema
      \ Eschema call s:Eschema(<q-args>)

function! s:Eschema(model_name)
  edit db/schema.sql

  if a:model_name != ''
    call search($'CREATE TABLE \zs{a:model_name} (')
  endif
endfunction

function! s:CompleteSchema(A, L, P)
  let tables = []

  for line in readfile('db/schema.sql')
    let table_name = matchstr(line, '^CREATE TABLE \zs\k\+\ze (')
    if table_name != ''
      call add(tables, table_name)
    endif
  endfor

  return join(tables, "\n")
endfunction

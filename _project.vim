runtime! projects/flask.vim

silent AckIgnore .micromamba/
silent TagsExclude .micromamba/*

let bacterial_growth_db_roots = ['.', 'flask_app']

call bacterial_growth_db#Init()

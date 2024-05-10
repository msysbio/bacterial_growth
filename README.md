# How to run the app


I fire the app by running 

```bash
streamlit run Welcome.py --server.fileWatcherType none
```


Remember the `.streamlit` folder and the `secrets.toml` and `config.toml` files.

```bash
[connections.BacterialGrowth]
dialect = "mysql"
username = ""
password = ""
host = ""
database = "BacterialGrowth"
```


When running locally, in linux, we need the `enableXsrfProtection` to be `false`,
[see](https://discuss.streamlit.io/t/file-upload-fails-with-error-request-failed-with-status-code-403/27143/35).






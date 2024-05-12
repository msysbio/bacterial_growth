from streamlit.runtime.scriptrunner import get_script_run_ctx

def clean_dashboard():
    ctx = get_script_run_ctx()
    print(ctx)
    print("=====================================")




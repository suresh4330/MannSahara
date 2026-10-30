"""Streamlit Cloud entrypoint alias for app.py."""
import runpy
import pathlib

# Execute app.py in the current namespace
app_path = pathlib.Path(__file__).parent / "app.py"
runpy.run_path(str(app_path), run_name="__main__")

import os

path = os.path.join(os.path.curdir, "webui","Home.py")
os.environ["STREAMLIT_THEME_BASE"] = "dark"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.system(f"streamlit run Home.py")
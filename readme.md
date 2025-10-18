python3 -m venv .venv

source .venv/bin/activate

pip install python-dotenv geopandas streamlit pydeck

streamlit run streamlit_map.py

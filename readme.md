python3 -m venv .venv

source .venv/bin/activate

pip install python-dotenv geopandas streamlit pydec

streamlit run streamlit_map.py
PORT=8000

uvicorn app.main:app --port PORT & streamlit run frontend/main.py
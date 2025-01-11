if [ "$FRONTEND" = "true" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    streamlit run frontend/main.py --server.port 8502 --server.address 0.0.0.0 &
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
fi

wait
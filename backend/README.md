# Grace Backend

This folder contains the Flask backend for the portfolio.

## Run locally

```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

## Deploy on Render

1. Create a new Web Service on Render and point it at the `backend` folder of this repo.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`

The API root is `/api/contacts`.

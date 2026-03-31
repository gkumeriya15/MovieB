"""Backend app config for WSGI servers"""
from app.main import app

# For deployment with Gunicorn, Waitress, etc.
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

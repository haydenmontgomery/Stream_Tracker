from app import create_app
from models import connect_db

app = create_app("stream_tracker_db")
connect_db(app)
import os
import logging
from flask import Flask
from datetime import datetime

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# In-memory storage for MVP
app.config['PROJECTS'] = []
app.config['TASKS'] = []
app.config['PROJECT_COUNTER'] = 1
app.config['TASK_COUNTER'] = 1

# Import routes after app creation to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

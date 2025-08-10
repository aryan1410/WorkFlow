from app import app
import auth  # Import auth to initialize Flask-Login
import routes  # Import routes to register them

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

#!/usr/bin/env python
"""Application entry point"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

# Get configuration from environment or use default
config_name = os.environ.get('FLASK_ENV') or 'development'
app = create_app(config_name)

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST') or '0.0.0.0'
    port = int(os.environ.get('FLASK_PORT') or 5000)
    debug = config_name == 'development'
    
    print(f"🚀 Starting Mini Supermarket API Server...")
    print(f"📍 Running on http://localhost:{port}")
    print(f"🔧 Environment: {config_name}")
    print(f"📌 Truy cập trình duyệt: http://localhost:{port}/api/health")
    
    app.run(host=host, port=port, debug=debug)

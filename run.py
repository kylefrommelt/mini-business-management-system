#!/usr/bin/env python3
"""
Mini Business Management System - Main Application Entry Point
"""
import os
from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug) 
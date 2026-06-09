import os


class Config:
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))

    # GravityZone: Basic Auth where username = API key, password = "" (empty)
    # The mock accepts any non-empty API key without validation.
    COMPANY_ID = os.environ.get('COMPANY_ID', 'gz-company-001')
    COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Business Corp')

    NUM_ENDPOINTS = int(os.environ.get('NUM_ENDPOINTS', 8))
    NUM_INCIDENTS = int(os.environ.get('NUM_INCIDENTS', 25))

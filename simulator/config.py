import os


class Config:
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8080))

    # TODO: choose the auth scheme your API uses and remove the other
    # Option A — API key in a header (e.g. Cato Networks: x-api-key)
    AUTH_API_KEY = os.environ.get('AUTH_API_KEY', 'change-me')
    # Option B — HTTP Basic Auth (e.g. ProofPoint TAP)
    AUTH_USERNAME = os.environ.get('AUTH_USERNAME', 'test-user')
    AUTH_PASSWORD = os.environ.get('AUTH_PASSWORD', 'test-secret')

    # TODO: add integration-specific settings below
    # Example:
    #   ACCOUNT_ID = os.environ.get('ACCOUNT_ID', '1234')
    #   MIN_ITEMS  = int(os.environ.get('MIN_ITEMS', 1))
    #   MAX_ITEMS  = int(os.environ.get('MAX_ITEMS', 10))

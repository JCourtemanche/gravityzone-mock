"""
TODO: Update service name throughout this file.
"""
import logging
from flask import Flask, jsonify
from config import Config

# TODO: import your blueprints (remove the example import when you replace it)
from routes.example import example_bp


def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO if Config.DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)

    # TODO: update service name
    logger.info("Starting XSIAM Simulator")

    # TODO: register your blueprints here
    app.register_blueprint(example_bp)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            # TODO: update service name
            'service': 'XSIAM Simulator',
            'version': '1.0.0',
        }), 200

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            # TODO: update service name and list real endpoints
            'service': 'XSIAM Simulator',
            'version': '1.0.0',
            'endpoints': {
                'GET /api/v1/records': 'Example endpoint — replace with real ones',
                'GET /health': 'Health check',
            },
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)

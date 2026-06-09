import logging
from flask import Flask, jsonify
from config import Config
from routes.jsonrpc import jsonrpc_bp
from routes.storage import storage_bp


def create_app():
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.INFO if Config.DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting Bitdefender GravityZone XSIAM Mock Server")

    app.register_blueprint(jsonrpc_bp)
    app.register_blueprint(storage_bp)

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'gravityzone-mock',
            'version': '1.0.0',
        }), 200

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'service': 'Bitdefender GravityZone XSIAM Mock Server',
            'version': '1.0.0',
            'protocol': 'JSON-RPC 2.0',
            'auth': 'HTTP Basic Auth (username=api_key, password=empty)',
            'endpoints': {
                'POST /api/<version>/jsonrpc/companies': 'getCompanyDetails',
                'POST /api/<version>/jsonrpc/network': 'getEndpointsList | getManagedEndpointDetails | getTaskStatus',
                'POST /api/<version>/jsonrpc/incidents': 'getIncidentsList | getIncident | updateIncidentNote | changeIncidentStatus | createIsolateEndpointTask | createRestoreEndpointFromIsolationTask',
                'POST /api/<version>/jsonrpc/investigation': 'startRetrieveInvestigationFileFromEndpoint | startCommandExecutionOnEndpoint | killProcess | collectInvestigationPackage | getInvestigationFileUrl',
                'POST /api/<version>/jsonrpc/internal': 'runPredefinedLiveSearchQuery | getLiveSearchQueryTaskResult',
                'POST /storage/<bucket>': 'Upload investigation file',
                'GET /storage/<bucket>/<filename>': 'Download investigation file',
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

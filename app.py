from flask import render_template, request, json
from flask_httpauth import HTTPBasicAuth
import os

from . import app, db
from .data import Account, Endpoint, Referer, ContractAddress
from datetime import datetime

host = os.getenv('HOST')
port = os.getenv('PORT')

auth_username = os.getenv('AUTH_USERNAME')
auth_password = os.getenv('AUTH_PASSWORD')
auth = HTTPBasicAuth()

@app.before_first_request
def create_table():
    db.create_all()

# Define the authentication method
@auth.verify_password
def verify_password(username, password):
    if username == auth_username and password == auth_password:
        return username

# public index endpoint with GET method
@app.route('/')
def index():
    return render_template('index.html')

# Provision endpoint with POST method
@app.route('/provision', methods=['POST'])
@auth.login_required
def provision():
    is_tester = request.headers['X-Qn-Testing'] == 'true'
    data = json.loads(request.data)

    # account data
    quicknode_id = data.get('quicknode-id', None)
    plan = data.get('plan', None)

    account = Account.query.filter_by(quicknode_id=quicknode_id).first()
    if account is None:
      app.logger.info('PROVISIONING new account')
      account = Account(quicknode_id, plan, is_tester)
      db.session.add(account)
      db.session.commit()

    # endpoint data
    endpoint_id = data.get('endpoint-id', None)
    chain = data.get('chain', None)
    network = data.get('network', None)
    wss_url = data.get('wss-url', None)
    http_url = data.get('http-url', None)
    contract_addresses = data.get('contract_addresses', None) # inconsistent naming
    referers = data.get('referers', None)

    endpoint = Endpoint.query.filter_by(account_id=account.id, endpoint_id=endpoint_id).first()
    if endpoint is None:
        app.logger.info('PROVISIONING new endpoint')
        endpoint = Endpoint(account.id, quicknode_id, endpoint_id, wss_url, http_url, chain, network, is_tester)
        db.session.add(endpoint)
        db.session.commit()

    for referer in referers:
        existing_referer = Referer.query.filter_by(referer= referer, endpoint_id = endpoint.id).first()
        if existing_referer is None:
            app.logger.info(f'Adding new referer to endpoint "{endpoint.id}", Referer: "{referer}"')
            new_referer = Referer(endpoint.id, referer)
            db.session.add(new_referer)
            db.session.commit()

    for address in contract_addresses:
        existing_address = ContractAddress.query.filter_by(address= address, endpoint_id = endpoint.id).first()
        if existing_address is None:
            app.logger.info(f'Adding new address to endpoint "{endpoint.id}", Address: "{address}"')
            new_address = ContractAddress(endpoint.id, address)
            db.session.add(new_address)
            db.session.commit()

    return {"status": "success", "dashboard-url": f"http://{host}:{port}/dashboard"}

# Update endpoint with PUT method
@app.route('/update', methods=['PUT'])
@auth.login_required
def update():
    data = json.loads(request.data)

    # account data
    quicknode_id = data.get('quicknode-id', None)
    endpoint_id = data.get('endpoint-id', None)
    plan = data.get('plan', None)
    # endpoint data
    chain = data.get('chain', None)
    network = data.get('network', None)
    wss_url = data.get('wss-url', None)
    http_url = data.get('http-url', None)
    contract_addresses = data.get('contract_addresses', None) # inconsistent naming
    referers = data.get('referers', None)

    app.logger.info(f'UPDATE quicknode_id "{quicknode_id}", endpoint_id: "{endpoint_id}"')

    account = Account.query.filter_by(quicknode_id=quicknode_id).first()
    if account is None:
        app.logger.info('[WARNING] account is not provisioned yet.')
        return {"status": "error","message": f'Unable to find account: "{quicknode_id}"'}
    account.plan = plan
    db.session.commit()

    endpoint = Endpoint.query.filter_by(account_id=account.id, endpoint_id=endpoint_id).first()
    if endpoint is None:
        app.logger.info('[WARNING] endpoint is not provisioned yet.')
        return {"status": "error","message": f'Unable to find endpoint: "{endpoint_id}"'}

    endpoint.chain = chain
    endpoint.network = network
    endpoint.wss_url = wss_url
    endpoint.http_url = http_url

    if referers is not None:
        endpoint.referers = []
    if contract_addresses is not None:
        endpoint.contract_addresses = []

    db.session.commit()

    for referer in referers:
        app.logger.info(f'Adding referer to endpoint "{endpoint.id}", Referer: "{referer}"')
        new_referer = Referer(endpoint.id, referer)
        db.session.add(new_referer)
        db.session.commit()

    for address in contract_addresses:
        app.logger.info(f'Adding address to endpoint "{endpoint.id}", Address: "{address}"')
        new_address = ContractAddress(endpoint.id, address)
        db.session.add(new_address)
        db.session.commit()

    return {"status": "success"}

# Deactivate endpoint with DELETE method
@app.route('/deactivate_endpoint', methods=['DELETE'])
@auth.login_required
def deactivate_endpoint():
    data = json.loads(request.data)
    quicknode_id = data.get('quicknode-id', None)
    endpoint_id = data.get('endpoint-id', None)
    app.logger.info(f'DEACTIVATE ENDPOINT quicknode_id "{quicknode_id}", endpoint_id: "{endpoint_id}"')

    account = Account.query.filter_by(quicknode_id=quicknode_id).first()
    if account is None:
        app.logger.info('[WARNING] account is not provisioned yet.')
        return {"status": "error","message": f'Unable to find account: "{quicknode_id}"'}

    endpoint = Endpoint.query.filter_by(account_id=account.id, endpoint_id=endpoint_id).first()
    if endpoint is None:
        app.logger.info('[WARNING] endpoint is not provisioned yet.')
        return {"status": "error","message": f'Unable to find endpoint: "{endpoint_id}"'}

    deprovisioned_at = datetime.utcnow()
    endpoint.deprovisioned_at = deprovisioned_at
    db.session.commit()
    return {"status": "success"}

# Deprovision endpoint with DELETE method
@app.route('/deprovision', methods=['DELETE'])
@auth.login_required
def deprovision():
    data = json.loads(request.data)
    quicknode_id = data.get('quicknode-id', None)
    endpoint_id = data.get('endpoint-id', None)
    app.logger.info(f'DEPROVISION quicknode_id "{quicknode_id}", endpoint_id: "{endpoint_id}"')

    account = Account.query.filter_by(quicknode_id=quicknode_id).first()
    if account is None:
        app.logger.info('[WARNING] account is not provisioned yet.')
        return {"status": "error","message": f'Unable to find account: "{quicknode_id}"'}

    deprovisioned_at = datetime.utcnow()
    account.deprovisioned_at = deprovisioned_at
    for endpoint in account.endpoints:
        endpoint.deprovisioned_at = deprovisioned_at
    db.session.commit()
    return {"status": "success"}

# RPC endpoint with POST method
@app.route('/rpc', methods=['POST'])
def rpc():
    return  {
        "id": 1,
        "error": {
        "code":-32001,
        "message":"Unauthenticated request"
        },
        "jsonrpc":"2.0"
    }

@app.route('/healthcheck')
def healthcheck():
    try:
        db.session.execute('SELECT 1')
        return {'status': 'ok'}
    except:
        return {'status': 'error'}

@app.route('/dashboard')
@auth.login_required
def dashboard():
    # use JWT token to decode account info and show dashboard
    return render_template('dash.html')

if __name__ == '__main__':
    app.run(host="localhost", port=port, debug=True)

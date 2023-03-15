from . import db
from datetime import datetime

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quicknode_id = db.Column(db.String(),unique=True)
    plan = db.Column(db.String())
    is_tester = db.Column(db.Boolean())
    endpoints = db.relationship('Endpoint', backref='account', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deprovisioned_at = db.Column(db.DateTime)

    def __init__(self, quicknode_id, plan, is_tester):
        self.quicknode_id = quicknode_id
        self.plan = plan
        self.is_tester = is_tester

    def __repr__(self):
        return f"{self.quicknode_id}"

class Endpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.String())
    wss_url = db.Column(db.String())
    http_url = db.Column(db.String())
    chain = db.Column(db.String())
    network = db.Column(db.String())
    is_tester = db.Column(db.Boolean())
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    referers = db.relationship('Referer', backref='endpoint', lazy=True, cascade="all,delete")
    contract_addresses = db.relationship('ContractAddress', backref='endpoint', lazy=True, cascade="all,delete")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deprovisioned_at = db.Column(db.DateTime)

    def __init__(self, account_id, quicknode_id, endpoint_id, wss_url, http_url, chain, network, is_tester):
        self.account_id = account_id
        self.quicknode_id = quicknode_id
        self.endpoint_id = endpoint_id
        self.wss_url = wss_url
        self.http_url = http_url
        self.chain = chain
        self.network = network
        self.is_tester = is_tester

    def __repr__(self):
        return f"{self.endpoint_id}"

class Referer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoint.id'), nullable=True)
    referer = db.Column(db.String())

    def __init__(self, endpoint_id, referer):
        self.endpoint_id = endpoint_id
        self.referer = referer

    def __repr__(self):
        return f"{self.referer}"

class ContractAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoint.id'), nullable=True)
    address = db.Column(db.String())

    def __init__(self, endpoint_id, address):
        self.endpoint_id = endpoint_id
        self.address = address

    def __repr__(self):
        return f"{self.address}"


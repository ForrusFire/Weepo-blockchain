from collections import OrderedDict

import binascii
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

import flask
from flask import request, jsonify, render_template


class Transaction:
    def __init__(self, sender, sender_private_key, recipient, amount):
        self.sender = sender
        self.sender_private_key = sender_private_key
        self.recipient = recipient
        self.amount = amount

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        """
        Returns the transaction as an ordered dictionary
        """
        return OrderedDict({'sender': self.sender,
                            'recipient': self.recipient,
                            'amount': self.amount})

    def sign_transaction(self):
        """
        Signs the transaction with the sender's private key and returns the signature
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')



app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/transactions/create', methods=['GET'])
def create_transaction():
    return render_template("create_transaction.html")

@app.route('/wallet/create', methods=['GET'])
def create_wallet():
    return render_template("create_wallet.html")


@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    """
    Creates a new wallet with a public and private key
    """
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()
    response = {
        'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
        'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
    }
    return jsonify(response), 200
    

@app.route('/transactions/make', methods=['POST'])
def make_transaction():
    sender = request.form['sender']
    sender_private_key = request.form['sender_private_key']
    recipient = request.form['recipient']
    amount = request.form['amount']

    transaction = Transaction(sender, sender_private_key, recipient, amount)

    response = {'transaction': transaction.to_dict(), 'signature': transaction.sign_transaction()}
    return jsonify(response), 200



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
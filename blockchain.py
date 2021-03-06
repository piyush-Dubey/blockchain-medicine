import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

class Blockchain():
    """docstring for Blockchain"""
    def __init__(self):
        
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash='1',proof=100)

    def register_node(self, address):
        
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index = current_index + 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof,previous_hash):   
        block = {
            'index':len(self.chain)+1,
            'timestamp' : time(),
            'transactions': self.current_transactions,
            'proof':proof,
            'previous_hash':previous_hash or self.hash(self.chain[-1]),
            'products': [0]*10,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self,bill_no,recipient_aadharno,ration_cardno,products):
        transaction={'bill_no':bill_no,
                          'recipient_aadharno':recipient_aadharno,
                          'ration_cardno':ration_cardno,
                          'products':products,
                          'amount':0,
                         }
        for product in products:
            transaction['amount']+=product['rate']*product['quantity']
        self.current_transactions.append(transaction)
        return self.last_block['index']+1
    
    """def new_transaction(self,sender,recipient,amount):
        self.current_transactions.append({'sender':sender,
                          'recipient':recipient,
                          'amount':amount,
                         })
        
        return self.last_block['index']+1"""


    @property
    def last_block(self):
        return self.chain[-1]
        
    @staticmethod
    def hash(block):        
        block_string=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
        
    def proof_of_work(self,last_proof):
        proof=0
        
        while self.valid_proof(last_proof,proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof,proof):
        guess=f'{last_proof}{proof}'.encode()
        guess_hash=hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=='0000'

            
app=Flask(__name__)

node_identifier = str(uuid4()).replace('-','')

blockchain=Blockchain()


@app.route('/mine',methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    
    """blockchain.new_transaction(
        sender = '0',
        recipient= node_identifier,
        amount=1,
    )"""

    previous_hash = blockchain.hash(last_block)
    block= blockchain.new_block(proof,previous_hash)

    for transaction in block['transactions']:
        for product in transaction['products']:
            block['products'][int(product['product_id'])]+=int(product['quantity'])
    response= {
        'message':'New Block Forged',
        'index' : block['index'],
        'transactions': block['transactions'],
        'proof':block['proof'],
        'products':block['products'],
        'previous_hash' : block['previous_hash'],
    }
    return jsonify(response),200
    
@app.route('/transaction/new', methods=['POST'])            
def new_transaction():

    values =  request.get_json()

    required = ['bill_no', 'recipient_aadharno', 'ration_cardno','products']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchian.new_transaction(values['bill_no'],values['recipient_aadharno'],values['ration_cardno'],values['products'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response={
        'chain':blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values=request.get_json()

    nodes=values.get('nodes')
    if nodes is None:
        return 'Error: Please supply valid list of nodes', 400
    for node in nodes:
        blockchain.register_node(node)
    response={
        'message':'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    #return 'adfsdfgs'
    return jsonify(response),201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
        'message': 'Our chain was replaced ',
        'new_chain':blockchain.chain
        }
    else:
        response={
        'message':'Our chain is authoritative',
        'chain':blockchain.chain
        }

    return jsonify(response), 200
              

@app.route('/', methods=['GET'])
def main():
    #register_node
    return "HELLO!!!<br>Instructions<br><br>Execute hasura for vitran app in console<br>Open the browser and go to https://vitran.fibber71.hasura-app.io/mine<br>You can observe the blocks for the blockchain generated<br>Refresh the page to create another block and so on<br>Go to https://vitran.fibber71.hasura-app.io/chain to view the complete blockchain<br><br>The new blocks are generated instantly due to low difficulty setting in proof of work for demonstration."

if __name__=='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p','--port',default=5000,type=int, help='port to listen on')
    args=parser.parse_args()
    ports = args.port
    app.run(host='0.0.0.0',port=ports)


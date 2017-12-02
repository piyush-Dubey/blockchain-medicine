import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import flask, jsonify, request

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
			if block['previous_hash'] != self.hash[last_block]:
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
            'previous_hash':previous_hash or self.hash(self.chain)
            }
        
        self.chain.append(block)
        return block

    	def new_transaction(self,sender,recipient,amount):

        	self.current_transactions.append({

            	'sender'=sender,
            	'recipient'=recipient,
            	'amount'=amount
            	)}
        
        	return self.last_block['index']+1


    	@property
    	def last_block(self):
        	return self.chain[-1]


    	@staticmethod
    	def hash(block):        
        	block_string=json.dumps(block,sort_keys=True).encode
        	return hashlib.sha256(block_string).hexdigest()

    	def proof_of_work(self,last_proof):

        	proof=0

        	while self.valid_proof(last_proof,proof) is False:
            	proof += 1
            
            	return proof

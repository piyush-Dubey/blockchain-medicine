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

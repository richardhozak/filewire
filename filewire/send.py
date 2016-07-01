import socket
import time
import pickle
import os
from functools import partial

class Sender:

	def __init__(self, client_ip, filename, verbose=False):
		self.sock = socket.socket()
		self.host = client_ip
		self.port = 6000
		self.filename = filename
		self.filesize = os.path.getsize(self.filename)
		self.verbose = verbose

	def run(self):
		self.send_metadata()
		if self.get_accept():
			self.send_file()
		
	def send_file(self):
		if self.verbose:
			print("sending file {} ({})".format(self.filename, self.filesize))

		sent = 0
		with open(self.filename, "rb") as f:
			for data in iter(partial(f.read, 4096), b''):
				self.sock.sendall(data)
				sent += len(data)
				print("progress: {0:0.1f} %".format((sent / self.filesize) * 100), end=("\r" if sent < self.filesize else "\n"))

		if self.verbose:
			print("completed")

	def send_metadata(self):
		metadata = {
			"filename": os.path.basename(self.filename),
			"size": os.path.getsize(self.filename)
		}

		if self.verbose:
			print("sending metadata")

		self.sock.send(pickle.dumps(metadata))

	def get_accept(self):
		return self.sock.recv(1) == b"Y"

	def __enter__(self):
		self._init_connection()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self._close_connection()

	def _init_connection(self):
		if self.verbose:
			print("connecting to {}:{}".format(self.host, self.port))

		while True:
			try:
				self.sock.connect((self.host, self.port))
				break
			except:
				time.sleep(1)
				pass

		if self.verbose:
			print("connected")

	def _close_connection(self):
		if self.verbose:
			print("closing connection")
		self.sock.close()

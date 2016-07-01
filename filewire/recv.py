import socket
import time
import pickle
import sys

class Receiver:

	def __init__(self, verbose=False):
		self.sock = socket.socket()
		self.port = 6000
		self.verbose = verbose

	def run(self):
		self.metadata = self.receive_metadata()
		
		if self.verbose:
			print("got metadata")

		user_accepts = self.get_user_accept()

		self.accept_file(user_accepts)

		if user_accepts:
			self.receive_file(self.metadata["filename"])

	def receive_file(self, filename):
		if self.verbose:
			print("receiving file {} ({})".format(self.metadata["filename"], self.metadata["size"]))

		with open(filename, "wb") as f:
			received = 0
			filesize = self.metadata["size"]
			while received < filesize:
				data = self.conn.recv(4096)
				received += len(data)
				f.write(data)
				print("progress: {0:0.1f} %".format((received / filesize) * 100), end=("\r" if received < filesize else "\n"))

		if self.verbose:
			print("completed")

	def receive_metadata(self):
		metadata_bytes = self.conn.recv(4096)
		return pickle.loads(metadata_bytes)

	def accept_file(self, accept=False):
		self.conn.send(b"Y" if accept else b"N")

	def get_user_accept(self):
		return input("accept file {} ({})? [Y/n]: ".format(self.metadata["filename"], self.humansize(self.metadata["size"]))) in ["y", "Y", "yes", ""]

	def __enter__(self):
		self._init_connection()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self._close_connection()

	def _init_connection(self):
		self.sock.bind(("", self.port))
		
		if self.verbose:
			print("listening on port {}".format(self.port))
		
		self.sock.listen(0)
		self.sock.settimeout(1)
		
		if self.verbose:
			print("accepting connection")

		while True:
			try:
				conn, addr = self.sock.accept()
				break
			except socket.timeout:
				pass
		
		if self.verbose:
			print("got connection from", addr)

		self.conn = conn

	def _close_connection(self):
		if self.verbose:
			print("closing connection")

		self.sock.close()

	def humansize(self, nbytes):
		suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
		if nbytes == 0:
			return '0 B'
		i = 0
		while nbytes >= 1024 and i < len(suffixes) - 1:
			nbytes /= 1024.
			i += 1
		f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
		return '%s %s' % (f, suffixes[i])

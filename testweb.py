#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import StringIO
import urllib


class  Hander(object):
	def app(self):
		pass

class  HTTPServer(object):

	def __init__(self, server_address, RequestHandleClass):		
		self.listen_socket = listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listen_socket.bind(server_address)
		listen_socket.listen(MAX_LISTEN)

	def server_forever(self):
		while True:
			self.client_connect, client_address = self.listen_socket.accept()
			self.handle_one_request()

	def handle_one_request(self):

		requst = self.client_connect.recv(1024)

		self.parse_request(requst)

		mname = 'do_' + self.requst_method

		method = getattr(self, mname)

		method()

		# env = self.get_environ()


	def do_GET(self):
		f = self.send_head()
		# if f:
		# 	try:
		# 		self.copyfile(f.getvalue())
		# 	finally:
		# 		f.close()
		

	def send_head(self):
		# 1 进入目录
		path = self.translate_path(self.path)

		# 2、如果是路径，列出文件列表
		if os.path.isdir(path):
			f = self.list_directory(path)
			self.client_connect.sendall(f.getvalue())
			self.client_connect.close()
			return f

		# 3、读取文件

		f = open(path, 'rb')
		self.client_connect.sendall(f.read())
		self.client_connect.close()
		return f

	def translate_path(self, path):
		cwdpath = os.getcwd()
		
		return cwdpath+path


	def list_directory(self, path):
		
		list = os.listdir(path)
		f = StringIO.StringIO()
		f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
		f.write("<html>\n<title>Directory listing</title>\n")
		f.write("<body>\n<h2>Directory listing for </h2>\n")
		f.write("<hr>\n<ul>\n")
		for name in list:
			fullname = os.path.join(path, name)
			displayname = linkname = name 
			if os.path.isdir(fullname):
				displayname = name + "/"
				linkname = name + "/"
			if os.path.islink(fullname):
				displayname = name + "@"
			f.write('<li><a href="%s">%s</a>\n' % (linkname, displayname))
		f.write('</ul>\n<hr>\n</body>\n</html>\n')
		length = f.tell()
		f.seek(0)
		return f
 

	def copyfile(self, sourc):
		self.client_connect.sendall(sourc)
		self.client_connect.close()



	def parse_request(self, text):
		request_line = text.splitlines()[0]
		request_line = request_line.rstrip('\r\n')
		(self.requst_method, self.path, self.version) = request_line.split()
		
	# def get_environ(self):
	# 	env = {}
 #        # The following code snippet does not follow PEP8 conventions
 #        # but it's formatted the way it is for demonstration purposes
 #        # to emphasize the required variables and their values
 #        #
 #        # Required WSGI variables
 #        env['wsgi.version']      = (1, 0)
 #        env['wsgi.url_scheme']   = 'http'
 #        env['wsgi.input']        = StringIO.StringIO(self.request_data)
 #        env['wsgi.errors']       = sys.stderr
 #        env['wsgi.multithread']  = False
 #        env['wsgi.multiprocess'] = False
 #        env['wsgi.run_once']     = False
 #        # Required CGI variables
 #        env['REQUEST_METHOD']    = self.request_method    # GET
 #        env['PATH_INFO']         = self.path              # /hello
 #        env['SERVER_NAME']       = self.server_name       # localhost
 #        env['SERVER_PORT']       = str(self.server_port)  # 8888
 #        return env

	def start_response(self, status, response_headers, exc_info=None):
		pass

	def finish_response(self, result):
		pass


SERVER_ADDRESS = (HOST, PORT) = '', 8888
MAX_LISTEN = 5


if __name__ == '__main__':
	http = HTTPServer(SERVER_ADDRESS, Hander)
   
	print ('server listen {host}:{port}...'.format(host=HOST, port=PORT))
	http.server_forever()
	

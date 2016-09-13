#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import StringIO
import urllib
import posixpath
import shutil
import sys
import time


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
			self.rfile = self.client_connect.makefile('rb', -1)
			self.wfile = self.client_connect.makefile('wb', 0)
			self.handle_one_request()

	def handle_one_request(self):
		requst = self.client_connect.recv(1024)

		self.parse_request(requst)

		mname = 'do_' + self.requst_method

		method = getattr(self, mname)

		method()
		self.wfile.flush()
        
		# env = self.get_environ()

	def do_GET(self):
		f = self.send_head()
		if f:
			try:
				self.copyfile(f, self.wfile)
			finally:
				f.close()
		

	def send_head(self):
		# 1 进入目录
		path = self.translate_path(self.path)

		# 2、如果是路径，列出文件列表
		if os.path.isdir(path):
			return self.list_directory(path)
			

		# 3、读取文件
		f = open(path, 'rb')
		return f

	def translate_path(self, path):
		path = path.split('?',1)[0]
		path = path.split('#',1)[0]
		trailing_slash = path.rstrip().endswith('/')
		path = posixpath.normpath(urllib.unquote(path))
		words = path.split('/')
		words = filter(None, words)
		path = os.getcwd()
		for word in words:
			drive, word = os.path.splitdrive(word)
			head, word = os.path.split(word)
			if word in (os.curdir, os.pardir): continue
			path = os.path.join(path, word)
		if trailing_slash:
			path += '/'
		
		return path


	def list_directory(self, path):
		
		list = os.listdir(path)
		f = StringIO.StringIO()
		f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n')
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
		self.send_response(200)
		encoding = sys.getfilesystemencoding()
		self.send_header("Content-type", "text/html; charset=%s" % encoding)
		self.send_header("Content-Length", str(length))
		self.end_headers()
		return f
 
	def copyfile(self, source, outputfile):
		shutil.copyfileobj(source, outputfile)

		if not self.wfile.closed:
			try:
				self.wfile.flush()
			except socket.error:
				pass

		self.wfile.close()
		self.rfile.close()
		self.client_connect.close()

	def parse_request(self, text):
		request_line = text.splitlines()[0]
		request_line = request_line.rstrip('\r\n')
		(self.requst_method, self.path, self.version) = request_line.split()

	def send_header(self, keyword, value):
		self.wfile.write("%s: %s\r\n" % (keyword, value))

	def end_headers(self):
		self.wfile.write("\r\n")

	def send_response(self, code, message=None):
		if message is None:
			if code in self.response:
				message = self.response[code][0]
			else:
				message = ''
		self.wfile.write("%s %d %s\r\n" % (self.protocol_version, code, message))
		self.send_header('Server', self.version_string())
		self.send_header('Date', self.date_time_string())

	def version_string(self):
		return "BaseHTTP/0.3" + " " + "Python/" + sys.version.split()[0]

	def date_time_string(self, timestamp=None):
		return "Tue, 13 Sep 2016 13:25:21 GMT"

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
	response = {
	  	100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
	}

	protocol_version = "HTTP/1.1"

SERVER_ADDRESS = (HOST, PORT) = '', 8888
MAX_LISTEN = 5


if __name__ == '__main__':
	http = HTTPServer(SERVER_ADDRESS, Hander)
   
	print ('server listen {host}:{port}...'.format(host=HOST, port=PORT))
	http.server_forever()
	

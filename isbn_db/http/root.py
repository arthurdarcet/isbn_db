import os.path
import tornado.web


staticdir = os.path.join(os.path.dirname(__file__), 'static')

urls = [
	(r'/()', tornado.web.StaticFileHandler, {'path': os.path.join(staticdir, 'index.html')}),
	(r'/static/(.+)', tornado.web.StaticFileHandler, {'path': staticdir}),
]

from server import FRESHandler
from http.server import HTTPServer

app = HTTPServer(("0.0.0.0", 8000), FRESHandler)

# For gunicorn WSGI
def application(environ, start_response):
    # This is a workaround - http.server doesn't support WSGI
    # We'll use a simple WSGI wrapper
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'FRES Backend is running. Use the API endpoints.']

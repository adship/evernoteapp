from evernote.api.client import EvernoteClient
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, urljoin

from constants import DEVELOPMENT_MODE, \
                      EVERNOTE_CONSUMER_KEY, \
                      EVERNOTE_CONSUMER_SECRET
from silent_webbrowser import SilentWebbrowser


RETURN_PATH = '/register'

PAGE_CONTENT = """<html>
<head>
    <style>
        body {
            background-color: #3f3f3f;
            font-family: "Lucida Console", Monaco, monospace;
        }
        .token {
            color: #6398cf;
            padding-right: 0.2em;
            font-weight: bold;
        }
        .prompt {
            color: #8ade37;
            padding-right: 0.2em;
            font-weight: bold;   
        }
        .text {
            color: #ffffff;
        }
    </style>
    <title>
        mininote
    </title>
</head>
<body>
    <div>
        <span class="prompt">mininote</span>
        <span class="token">~$</span></span>
        <span class="text"><b>Mininote login complete</b></span>
    </div>
    <div>
        <span class="prompt">mininote</span>
        <span class="token">~$</span></span>
        <span class="text">You may close this page and return to the terminal.</span>
    </div>
</body>
</html>"""

def get_auth_token():
    """
    Run through the Evernote OAuth procedure

    :returns: User token string
    """
    # Create an HTTP server on a spare port
    httpd = MininoteHTTPServer(('127.0.0.1', 0), MininoteHTTPRequestHandler)
    callbackurl = urljoin("http://{}:{}".format(*httpd.server_address), RETURN_PATH)

    client = EvernoteClient(consumer_key=EVERNOTE_CONSUMER_KEY,
                            consumer_secret=EVERNOTE_CONSUMER_SECRET,
                            sandbox=DEVELOPMENT_MODE)

    request_token = client.get_request_token(callbackurl)

    authorize_url = client.get_authorize_url(request_token)
    print 'Please login at the following url:\n{}'.format(authorize_url)

    # Open browser to auth page
    SilentWebbrowser(authorize_url).start()

    # Wait until browser is redirected
    httpd.server_activate()
    while httpd.auth_path is None:
        httpd.handle_request()
    httpd.server_close()

    def parse_query_string(authorize_url):
        query_params = urlparse(authorize_url).query
        return dict(kv.split('=') for kv in query_params.split('&'))

    vals = parse_query_string(httpd.auth_path)
    if 'oauth_verifier' not in vals:
        raise OAuthError('There was an error logging in.  Please try again.')
    return client.get_access_token(request_token['oauth_token'],
                                   request_token['oauth_token_secret'],
                                   vals['oauth_verifier'])

class OAuthError(Exception):
    """Error in OAuth procedure"""

class MininoteHTTPServer(HTTPServer):
    """HTTPServer for static OAuth response page"""

    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.auth_path = None

class MininoteHTTPRequestHandler(BaseHTTPRequestHandler):
    """Serve static OAuth response page"""

    def do_GET(self):
        if urlparse(self.path).path == RETURN_PATH:
            self.server.auth_path = self.path
            self.send_response(200)
            self.send_header("Content-type", "text/html;")
            self.send_header("Content-Length", len(PAGE_CONTENT))
            self.end_headers()
            self.wfile.write(PAGE_CONTENT)

    def log_message(self, format, *args):
        """Do nothing to mute output."""
        pass

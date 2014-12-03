from evernote.api.client import EvernoteClient
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse

from constants import DEVELOPMENT_MODE, \
                      EVERNOTE_CONSUMER_KEY, \
                      EVERNOTE_CONSUMER_SECRET
from silent_webbrowser import SilentWebbrowser


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
        <span class="text">Proceed to the nearest terminal</span>
    </div>
</body>
</html>"""

def get_auth_token():
    """
    Run through the Evernote OAuth procedure

    :returns: User token string
    """
    # Create an HTTP server on a spare port
    httpd = HTTPServer(('127.0.0.1', 0), MininoteHTTPRequestHandler)
    callbackurl = "http://{}:{}".format(*httpd.server_address)

    client = EvernoteClient(consumer_key = EVERNOTE_CONSUMER_KEY,
                            consumer_secret = EVERNOTE_CONSUMER_SECRET,
                            sandbox = DEVELOPMENT_MODE)

    request_token = client.get_request_token(callbackurl)

    authorize_url = client.get_authorize_url(request_token)
    print 'Please login at the following url:\n{}'.format(authorize_url)

    # Open browser to auth page
    SilentWebbrowser(authorize_url).start()

    # Wait until browser is redirected
    httpd.server_activate()
    httpd.handle_request()
    httpd.server_close()

    def parse_query_string(authorize_url):
        query_params = urlparse(authorize_url).query
        return dict(kv.split('=') for kv in query_params.split('&'))

    vals = parse_query_string(httpd.path)
    return client.get_access_token(request_token['oauth_token'],
                                   request_token['oauth_token_secret'],
                                   vals['oauth_verifier'])

class MininoteHTTPRequestHandler(BaseHTTPRequestHandler):
    """Serve static OAuth response page"""

    def do_GET(self):
        self.server.path = self.path
        self.send_response(200)
        self.send_header("Content-type", "text/html;")
        self.send_header("Content-Length", len(PAGE_CONTENT))
        self.end_headers()
        self.wfile.write(PAGE_CONTENT)

    def log_message(self, format, *args):
        """Do nothing to mute output."""
        pass

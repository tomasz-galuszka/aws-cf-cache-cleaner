import os

__author__ = 'galuszkat'

AWS_ACCESS_KEY = ''  # os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = ''  # os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SERVICE_ID = ''
AWS_REGION = 'us-east-1'
AWS_SERVICE = 'cloudfront'
AWS_HOST = 'cloudfront.amazonaws.com'

PATH = '/2015-04-17/distribution/%s/invalidation/' % AWS_SERVICE_ID
CONTENT_TYPE = 'text/xml'
CHARSET = 'utf-8'
ALGORITHM = 'AWS4-HMAC-SHA256'

REQUEST_BODY = 'templates/request_invalidate_body.xml'

proxies = {
    'https': os.environ.get('HTTPS_PROXY'),
    'http': os.environ.get('HTTPS_PROXY')
}

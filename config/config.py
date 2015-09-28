__author__ = 'galuszkat'

AWS_ACCESS_KEY = 'AKIAICDQQHI5LLJT4L4A'  # os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = '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'  # os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SERVICE_ID = 'E28W3Y5IKJSYFV'
AWS_REGION = 'us-east-1'
AWS_SERVICE = 'cloudfront'
AWS_HOST = 'cloudfront.amazonaws.com'

PATH = '/2015-04-17/distribution/%s/invalidation/' % AWS_SERVICE_ID
CONTENT_TYPE = 'text/xml'
CHARSET = 'utf-8'
ALGORITHM = 'AWS4-HMAC-SHA256'
REQUEST_BODY = 'templates/request_invalidate_body.xml'

import hashlib
import hmac


def create_signed_headers():
    return 'content-type;host;x-amz-date'


def create_hashed_payload(request_body):
    return hashlib.sha256(request_body).hexdigest()


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


class Authorization(object):
    def __init__(self, _date, date_stamp, algorithm, region, service):
        super(Authorization, self).__init__()
        self._date = _date
        self.date_stamp = date_stamp
        self.algorithm = algorithm
        self.region = region
        self.service = service

    # ************* Task 1: Create a Canonical Request For Signature Version 4 ************************************
    def create_canonical_request_form(self, request_body, method, path, content_type, charset, host, query_string):
        canonical_http_method = method
        canonical_uri = path
        canonical_query_string = query_string

        canonical_headers = 'content-type:' + content_type + '; charset=' + charset + '\n' \
                            + 'host:' + host + '\n' \
                            + 'x-amz-date:' + self._date + '\n'

        signed_headers = create_signed_headers()

        hashed_payload = create_hashed_payload(request_body)  # empty for get requests

        return canonical_http_method + '\n' \
               + canonical_uri + '\n' \
               + canonical_query_string + '\n' \
               + canonical_headers.lower() + '\n' \
               + signed_headers + '\n' \
               + hashed_payload

    @staticmethod
    def create_hashed_canonical_request_form(canonical_request_form):
        return hashlib.sha256(canonical_request_form).hexdigest()

    # ************* Task 2: Create a String to Sign for Signature Version 4 ***************************************
    def generate_credential_scope(self):
        credential_scope = self.date_stamp + '/' + self.region + '/' + self.service + '/' + 'aws4_request'
        return credential_scope

    def create_string_to_sign4(self, request_body, method, path, content_type, charset, host, query_string):
        canonical_request_form = self.create_canonical_request_form(request_body, method, path, content_type, charset,
                                                                    host, query_string)
        canonical_request_hashed = self.create_hashed_canonical_request_form(canonical_request_form)
        credential_scope = self.generate_credential_scope()

        return self.algorithm + '\n' + self._date + '\n' + credential_scope + '\n' + canonical_request_hashed

    # ************* Task 3: Calculate the AWS Signature Version 4 *************************************************
    def calculate_aws_signature_key4(self, aws_secret_access_key):
        key_date = sign(('AWS4' + aws_secret_access_key).encode('utf-8'), self.date_stamp)
        key_region = sign(key_date, self.region)
        key_service = sign(key_region, self.service)
        key_signing = sign(key_service, 'aws4_request')

        return key_signing

    def calculate_aws_signature4(self, aws_secret_access_key, request_body, method, path, content_type, charset, host,
                                 query_string):
        signature_key = self.calculate_aws_signature_key4(aws_secret_access_key)
        string_to_sign = self.create_string_to_sign4(request_body, method, path, content_type, charset, host,
                                                     query_string)
        return hmac.new(signature_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    # ************* Task 4: Add the Signing Information to the Request**********************************************
    def create_authorization_header(self, aws_access_key, aws_secret_access_key, request_body, method, path,
                                    content_type, charset, host, query_string):
        credential_scope = self.generate_credential_scope()
        signed_headers = create_signed_headers()
        signature = self.calculate_aws_signature4(aws_secret_access_key, request_body, method, path, content_type,
                                                  charset, host, query_string)
        return self.algorithm + ' Credential=' + aws_access_key + '/' + credential_scope + ',' + ' SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

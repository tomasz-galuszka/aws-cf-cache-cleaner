import datetime
import time
import os
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement
import sys

import requests

from auth.authorization import Authorization
from config.config import ALGORITHM, AWS_SERVICE, REQUEST_BODY, AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY, AWS_HOST, \
    CONTENT_TYPE, CHARSET, PATH, AWS_REGION, proxies


class Invalidator(object):
    def __init__(self):
        super(Invalidator, self).__init__()
        t = datetime.datetime.utcnow()
        self._DATE = t.strftime('%Y%m%dT%H%M%SZ')
        self.DATE_STAMP = t.strftime('%Y%m%d')
        self.auth = Authorization(self._DATE, self.DATE_STAMP, ALGORITHM, AWS_REGION, AWS_SERVICE)

    @staticmethod
    def log_headers(headers):
        for header in headers:
            print header + ': ' + headers[header]
        print ''

    @staticmethod
    def prepare_request_body(items):
        ElementTree.register_namespace('', 'http://cloudfront.amazonaws.com/doc/2015-04-17/')

        xml_doc = ElementTree.parse(REQUEST_BODY)
        root_element = xml_doc.getroot()

        paths_element = root_element[0]
        quantity_element = paths_element[0]
        items_element = paths_element[1]
        caller_reference_element = root_element[1]

        for item in items:
            item_path_element = SubElement(items_element, 'Path')
            item_path_element.text = item

        quantity_element.text = str(len(items))
        caller_reference_element.text = str(time.time())

        ElementTree.ElementTree(root_element).write(caller_reference_element.text, encoding="utf-8",
                                                    xml_declaration=True,
                                                    default_namespace="")

        tmp_file = open(caller_reference_element.text)
        xml_content = tmp_file.read()
        tmp_file.close()
        os.remove(caller_reference_element.text)

        return xml_content

    @staticmethod
    def check_aws_keys():
        if AWS_ACCESS_KEY is None or AWS_SECRET_ACCESS_KEY is None:
            print 'No aws access key is available.'
            sys.exit()

    def generate_request_headers(self, authorization_header_value):
        return {
            'Host': AWS_HOST,
            'Authorization': authorization_header_value,
            'Content-Type': CONTENT_TYPE + '; charset=' + CHARSET,
            'X-Amz-Date': self._DATE
        }

    def invalidate_cache(self, items):
        request_body = self.prepare_request_body(items)

        auth_header_value = self.auth.create_authorization_header(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, request_body,
                                                                  'POST',
                                                                  PATH,
                                                                  CONTENT_TYPE, CHARSET, AWS_HOST, '')

        headers = self.generate_request_headers(auth_header_value)
        endpoint = 'https://' + AWS_HOST + PATH

        print endpoint
        self.log_headers(headers)

        try:
            response = requests.post(url=endpoint, data=request_body, headers=headers, proxies=proxies)
            if response.status_code == requests.codes.ok:
                xml_doc = ElementTree.ElementTree(ElementTree.fromstring(response.text))
                root_element = xml_doc.getroot()
                invalidaiton_id = root_element[0].text
                invalidaiton_status = root_element[1].text
                invalidaiton_created_time = root_element[3].text

                print invalidaiton_id
                print invalidaiton_status
                print invalidaiton_created_time

                return invalidaiton_id
            else:
                print response.text
                return None
        except Exception as e:
            print e.message
            return None

    def get_invalidation_list(self):
        print 'Trying to get invalidation list ...'

        request_body = ''
        query_string = ''  # ?Marker=value&MaxItems=value see http://docs.aws.amazon.com/AmazonCloudFront/latest/APIReference/ListInvalidation.html

        auth_header_value = self.auth.create_authorization_header(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, request_body,
                                                                  'GET',
                                                                  PATH,
                                                                  CONTENT_TYPE, CHARSET, AWS_HOST, query_string)
        headers = self.generate_request_headers(auth_header_value)
        endpoint = 'https://' + AWS_HOST + PATH

        print endpoint
        self.log_headers(headers)

        try:
            response = requests.get(url=endpoint, headers=headers, proxies=proxies)
            if response.status_code == requests.codes.ok:
                xml_doc = ElementTree.ElementTree(ElementTree.fromstring(response.text))
                root_element = xml_doc.getroot()
                quantity_element = root_element[3]
                print 'Quantity: ' + quantity_element.text + '\n'

                items_element = root_element[4]
                for child in items_element:
                    print 'Id: ' + str(child[0].text)
                    print 'CreateTime: ' + str(child[1].text)
                    print 'Status: ' + str(child[2].text)
                    print '----------------------------------------'
            else:
                print response.text
            return response
        except Exception as e:
            print e.message
            return None

    def get_invalidation(self, invalidation_id):
        print 'Trying to get invalidation %s ...' % str(invalidation_id)

        request_body = ''
        query_string = ''

        auth_header_value = self.auth.create_authorization_header(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, request_body,
                                                                  'GET',
                                                                  PATH + invalidation_id,
                                                                  CONTENT_TYPE, CHARSET, AWS_HOST, query_string)
        headers = self.generate_request_headers(auth_header_value)
        endpoint = 'https://' + AWS_HOST + PATH + '/' + invalidation_id

        print endpoint
        self.log_headers(headers)

        try:
            response = requests.get(url=endpoint, headers=headers , proxies=proxies)
            if response.status_code == requests.codes.ok:
                xml_doc = ElementTree.ElementTree(ElementTree.fromstring(response.text))
                root_element = xml_doc.getroot()

                print 'Id: ' + root_element[0].text
                print 'Status: ' + root_element[1].text
                print 'CreateTime: ' + root_element[2].text

                return root_element[1].text
            else:
                print response.text
                return None
        except Exception as e:
            print e.message
            return None

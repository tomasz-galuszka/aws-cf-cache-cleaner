import datetime
import optparse
import time
import os
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement
import sys

import requests

from auth.authorization import Authorization

AWS_ACCESS_KEY = 'AKIAICDQQHI5LLJT4L4A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_SERVICE_ID = 'E28W3Y5IKJSYFV'
AWS_REGION = 'us-east-1'
AWS_SERVICE = 'cloudfront'
AWS_HOST = 'cloudfront.amazonaws.com'

PATH = '/2015-04-17/distribution/%s/invalidation/' % AWS_SERVICE_ID
CONTENT_TYPE = 'text/xml'
CHARSET = 'utf-8'
ALGORITHM = 'AWS4-HMAC-SHA256'
REQUEST_BODY = 'templates/request_invalidate_body.xml'

t = datetime.datetime.utcnow()
_DATE = t.strftime('%Y%m%dT%H%M%SZ')
DATE_STAMP = t.strftime('%Y%m%d')

auth = Authorization(_DATE, DATE_STAMP, ALGORITHM, AWS_REGION, AWS_SERVICE)


def log_headers(headers):
    for header in headers:
        print header + ': ' + headers[header]
    print ''


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

    ElementTree.ElementTree(root_element).write(caller_reference_element.text, encoding="utf-8", xml_declaration=True,
                                                default_namespace="")

    tmp_file = open(caller_reference_element.text)
    xml_content = tmp_file.read()
    tmp_file.close()
    os.remove(caller_reference_element.text)

    return xml_content


def check_aws_keys():
    if AWS_ACCESS_KEY is None or AWS_SECRET_ACCESS_KEY is None:
        print 'No aws access key is available.'
        sys.exit()


def generate_request_headers(authorization_header_value):
    return {
        'Host': AWS_HOST,
        'Authorization': authorization_header_value,
        'Content-Type': CONTENT_TYPE + '; charset=' + CHARSET,
        'X-Amz-Date': _DATE
    }


def invalidate_cache(items):
    print 'Trying to invalidate files:\n'
    for item in items:
        print item
    print '\n'

    request_body = prepare_request_body(items)

    auth_header_value = auth.create_authorization_header(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, request_body, 'POST',
                                                         PATH,
                                                         CONTENT_TYPE, CHARSET, AWS_HOST, '')

    headers = generate_request_headers(auth_header_value)
    endpoint = 'https://' + AWS_HOST + PATH

    print endpoint
    log_headers(headers)

    try:
        response = requests.post(url=endpoint, data=request_body, headers=headers)
        if response.status_code == requests.codes.ok:
            xml_doc = ElementTree.parse(response.text)
            root_element = xml_doc.getroot()

            print response.text
        else:
            print response.text

        return response
    except Exception as e:
        print e.message
        return None


def get_invalidation_list():
    print 'Trying to get invalidation list ...'

    request_body = ''
    query_string = ''  # ?Marker=value&MaxItems=value see http://docs.aws.amazon.com/AmazonCloudFront/latest/APIReference/ListInvalidation.html

    auth_header_value = auth.create_authorization_header(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, request_body, 'GET',
                                                         PATH,
                                                         CONTENT_TYPE, CHARSET, AWS_HOST, query_string)
    headers = generate_request_headers(auth_header_value)
    endpoint = 'https://' + AWS_HOST + PATH

    print endpoint
    log_headers(headers)

    try:
        response = requests.get(url=endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            xml_doc = ElementTree.ElementTree(ElementTree.fromstring(response.text))
            root_element = xml_doc.getroot()
            quantity_element = root_element[3]
            print 'Quantity: ' + quantity_element.text

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


def get_invalidation(invalidation_id):
    print 'Trying to get invalidation %s ...' % str(invalidation_id)

    request_body = ''
    query_string = ''

    auth_header_value = auth.create_authorization_header(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, request_body, 'GET',
                                                         PATH + invalidation_id,
                                                         CONTENT_TYPE, CHARSET, AWS_HOST, query_string)
    headers = generate_request_headers(auth_header_value)
    endpoint = 'https://' + AWS_HOST + PATH + '/' + invalidation_id

    print endpoint
    log_headers(headers)

    try:
        response = requests.get(url=endpoint, headers=headers)
        if response.status_code == requests.codes.ok:
            xml_doc = ElementTree.ElementTree(ElementTree.fromstring(response.text))
            root_element = xml_doc.getroot()

            print 'Id: ' + root_element[0].text
            print 'Status: ' + root_element[1].text
            print 'CreateTime: ' + root_element[2].text

        else:
            print response.text
        return response
    except Exception as e:
        print e.message
        return None


def main():
    """
    -a [invalidation_info<invalidation_id> | invalidation_info_list | invalidate<items_file_path> ]
    """
    p = optparse.OptionParser()
    p.add_option('--action', '-a', default="invalidation_info_list")
    options, arguments = p.parse_args()

    check_aws_keys()
    if options.action == 'invalidation_info':
        if len(arguments) == 1:
            get_invalidation(arguments[0])
        else:
            print 'Action requires invalidation_id as argument'

    elif options.action == 'invalidation_info_list':
        get_invalidation_list()

    elif options.action == 'invalidate':
        if len(arguments) == 1:

            changed_files_path = arguments[0]
            input_files = []
            with open(changed_files_path, 'r') as f:
                for line in f:
                    if len(line.strip()) == 0:
                        continue
                    input_files.append(line.strip())

            invalidate_cache(input_files)
        else:
            print 'Action requires changed file path as argument'
    else:
        print '\nInvalid arguments: \n\n' + \
              os.path.basename(
                  __file__) + ' -a [invalidation_info <invalidation_id>|invalidation_info_list|invalidate]\n'


if __name__ == '__main__':
    main()

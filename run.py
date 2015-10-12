import optparse
import time

from invalidator.invalidator import Invalidator


def read_input_files(file_arguments):
    if file_arguments is None or len(file_arguments) == 0:
        return []
    result = []

    mime_type = file_arguments[0]

    i = 0
    for item in file_arguments:
        if i == 0:
            i += 1
            continue
        if len(item) == 0:
            continue
        if item == 'version.txt':
            continue

        result.append("/" + mime_type + "/" + item)
        i += 1

    return result


def wait(seconds):
    time.sleep(seconds)


def main():
    """
    -a [invalidation_info<invalidation_id> | invalidation_info_list | invalidate<items_file_path> ]
    """
    p = optparse.OptionParser()
    p.add_option('--action', '-a')
    options, arguments = p.parse_args()

    if options.action == 'invalidation_info':
        if len(arguments) == 1:
            invalidator = Invalidator()
            invalidator.check_aws_keys()
            invalidator.get_invalidation(arguments[0])
        else:
            raise Exception('Action requires invalidation_id as argument')

    elif options.action == 'invalidation_info_list':
        invalidator = Invalidator()
        invalidator.check_aws_keys()
        invalidator.get_invalidation_list()

    elif options.action == 'invalidate':
        if len(arguments) < 2:
            raise Exception('Action requires file as first argument and mime type as second argument.')

        input_files = read_input_files(arguments)
        if len(input_files) == 0:
            raise Exception('Empty file list')

        invalidator = Invalidator()
        invalidator.check_aws_keys()

        invalidation_id = invalidator.invalidate_cache(input_files)

        if invalidation_id is None:
            raise Exception('Invalid invalidation_id')

        while True:
            invalidator = Invalidator()
            invalidator.check_aws_keys()

            invalidation_status = invalidator.get_invalidation(invalidation_id)

            if invalidation_status is None:
                raise Exception('Invalid invalidation status')
            if invalidation_status == 'Completed':
                print 'OK'
                break
            wait(60)

    else:
        p.print_help()
        raise Exception(
            '    [invalidation_info <invalidation_id>|invalidation_info_list|invalidate <content_type><files>]\n' \
            '\n   **Example: python run.py -a invalidation_info_list **\n')


if __name__ == '__main__':
    main()

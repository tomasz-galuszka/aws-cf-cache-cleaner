import optparse

from invalidator.invalidator import Invalidator


def main():
    """
    -a [invalidation_info<invalidation_id> | invalidation_info_list | invalidate<items_file_path> ]
    """
    p = optparse.OptionParser()
    p.add_option('--action', '-a')
    options, arguments = p.parse_args()

    invalidator = Invalidator()
    invalidator.check_aws_keys()
    if options.action == 'invalidation_info':
        if len(arguments) == 1:
            invalidator.get_invalidation(arguments[0])
        else:
            print 'Action requires invalidation_id as argument'

    elif options.action == 'invalidation_info_list':
        invalidator.get_invalidation_list()

    elif options.action == 'invalidate':
        if len(arguments) == 1:

            changed_files_path = arguments[0]
            input_files = []
            with open(changed_files_path, 'r') as f:
                for line in f:
                    if len(line.strip()) == 0:
                        continue
                    input_files.append(line.strip())

            invalidator.invalidate_cache(input_files)
        else:
            print 'Action requires changed file path as argument'
    else:
        p.print_help()
        print '    [invalidation_info <invalidation_id>|invalidation_info_list|invalidate <file_list_path>]\n' \
              '\n   **Example: python run.py -a invalidation_info_list **\n'


if __name__ == '__main__':
    main()

import sys, getopt


def parse_args(data):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "fh:w:d:", ["fullscreen", "height=", "width=",
                                                               "dir", "help"])
    except getopt.GetoptError:
        print('main.py [-f --fullscreen] [-h num] [-w num] [--width=num] [--height=num] [-d dir] '
              '--dir=dir')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-f', '--fullscreen']:
            data.options['fullscreen'] = True
        elif opt in ['-h', '--height']:
            data.options['height'] = arg
        elif opt in ['-w', '--width']:
            data.options['width'] = arg
        elif opt in ['-d', '--dir']:
            data.options['dir'] = arg
        elif opt in ['--help']:
            data.options['help'] = True
    data.options['args'] = args

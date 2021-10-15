Python user interface
=====================


check python version, 3.5 is required for subprocess timeout

    MIN_PYTHON = (3, 5)
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

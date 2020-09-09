Shell script:

Simple call
    try:
        subprocess.check_output(
            ['cryptsetup', 'luksDump', Device],
            stderr=open(os.devnull)
        )

    except subprocess.CalledProcessError as E:
        if E.returncode == 4:
            raise KnownError(
                'Could not find block device or image file ' \
                '"{0}"'.format(Device), os.EX_CANTCREAT
            )
        else:
            raise

Call command, read input line by line

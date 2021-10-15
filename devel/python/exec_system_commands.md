Python system commands
======================

Retrieve command output, handle bad exit command and ignore unicode errors

    try:
        out = subprocess.check_output(['megacli', '-AdpAllInfo', 'aAll'])
    except subprocess.CalledProcessError as err:
        print('Error {} running "{}": {}'.format(err.returncode, ' '.join(err.cmd), err.output))
        sys.exit(err.returncode)
    else:
        return out.decode('utf-8', errors='ignore').splitlines()


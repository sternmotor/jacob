Python error handling
=====================




print exception message (no stack trace)

    try:
        some-dangerous-code

    except Exception as err:
        err_text = getattr(err, 'message', repr(err))
        log.error(err_text)

log exception with stack trace


    try:
        some-dangerous-code

    except Exception:
        log.error('Unexpected script error, debug info:', exc_info=True)


retrieve exception stack trace as multi-line string

    import traceback 
    try:
        some-dangerous-code
    except Exception:
        sys.stderr.write(traceback.format_exc())


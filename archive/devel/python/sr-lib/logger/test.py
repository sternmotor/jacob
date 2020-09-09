#!/usr/bin/python



from pt.logger import Logger, LoggerError
import logging
import sys


try:
    mylog = Logger(
        #__name__ of module, self.__class__.__name__ of class 
        name="fly.logging.test_loggi"        ,
        file_level   = logging.WARNING     , 
        file_file    = "test.log"          , 
        level   = logging.INFO        , 
#        mail_level   = logging.CRITICAL    ,
#        mail_sender  = "fly@test.de"       ,
#        mail_addrs   = [ "g.mann@secu-ring.de" ],
#        mail_subject = "hallo!!"           ,
    )

    mylog.debug("debug message")
    mylog.info("info message")
    mylog.warn("warn message")
    mylog.error("error message")
    mylog.critical("critical message")

except LoggerError, emsg:
    print emsg
    sys.exit( 1 )

    # see http://sgillies.net/blog/832/python-logging/
#    log = setup( f_level = None, c_level = logging.INFO, m_level=None )

    a = """
    # make a script that uses a class in a verbose (all logged info) mode or a quieter (logged errors only) mode

    # Create a logger
    log = logging.getLogger('file-patcher')

    # Example of reusable code
    class FilePatcher(object):
        def __call__(self):
            for infilename in glob.glob('*.xml'):
                tree = etree.parse(infilename)
                log.info('Opening file %s.', infilename)

    # Script
    if __name__ == '__main__':
        # Get the file patching logger
        log = logging.getLogger('file-patcher')

        # Logging configuration, to stdout in this case
        console = logging.StreamHandler()
        log.addHandler(console)

        if verbose:
            log.setLevel(logging.INFO)
        else:
            log.setLevel(logging.ERROR)

        # Process data
        patch_files = FilePatcher()
        patch_files()
    """


# see NTEventLogHandler


# configure root logger in main prog (by calling logging.getLogger() with no arguments)
# log = setup (name = None)

# configure module.class loggers for each module and class
# self.log = setup ( name = '%s.%s' % (__name__, self.__class__.__name__) )


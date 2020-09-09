
def parser_add_localdst(Parser):
    Parser.add_argument('TargetLocation', metavar='URL::DUMP_DIR', action='store',
        help="""
            Destination for backup dump. Files in this directory are
            replaced by new backup data . During backup, the old data
            are beeing held in <DUMP_DIR>.bak directory. In case URL is 
            specified, dump action is executed remotely
        """
    )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# REMOTE OPERATION AND HELP 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REMOTE_HELP_DESCRIPTION = """
REMOTE OPERATION
    In case "URL/" parameter is specified for DUMP|SRC|DST directories, script 
    actions take place at specifed remote network location.

    Only one of SRC or DST can be located remotely. Thus, "pull" and "push" 
    operation modes can be distinguished where push mode is less secure in 
    bigger environments:

        * pull mode: source server is remote, backup server local or
        * push mode: backup data is pushed to backup server

    Remote URL specification:
        [protocol://][[USER[%PASSWORD]@]HOST[:PORT]]

        * Example1: backupuser@backup.de:2222::relative_path
        * Example2: backupuser@backup.de:2222::/absolute_path

        * As of now, only ssh protocol is supported so there is no need to 
          specify "ssh://" explicitly.
        * specifying PASSWORD here is not encouraged, use ssh keys
"""

# ----------------------------------------------------------------------------
class LocationStore():
# ----------------------------------------------------------------------------
    """
    Analyse given url + directory path, store login data as python object
    For ssh connections, passwords are not supported. Use ssh keys.

    Usage: location = Location([protocol://][[USER[%PASSWORD]@]HOST[:PORT]]) 
           print(location.IsRemote)
           Result = location.run( 'ls /boot' )

            print location.desc    # "locally" or "at remote host <host>"

    """
    def __init__(self, LocationExpr):
        """Analyse location string, store values"""

        NoProtocol = self._find_protocol(LocationExpr)
        Url = self._find_path(NoProtocol)
        HostPort = self._find_logindata( Url )
        self._find_address( HostPort)

        # prepare location announcement
        self.Descr = self.IsRemote and 'at host "%s"' % self.host or 'locally'

        log.debug('Location info: %s' % self.__dict__ )

    def _find_protocol(self, LocationExpr):
        log.debug('Analysing location expression "%s"' % LocationExpr)
        try:
            self.Protocol, NoProtocol = LocationExpr.split('://')
        except ValueError:
            self.Protocol = DEFAULT_PROTOCOL
            NoProtocol = LocationExpr
        if not self.Protocol in VALID_PROTOCOLS:
            raise KnownError(
                'Bad protocol "%s" in location "%s", expecting one of %s'        
                % (self.Protocol, LocationExpr, ', '.join(VALID_PROTOCOLS))
            )
        return NoProtocol

    def _find_path(self, NoProtocol ):
        Url = NoProtocol.split('/')[0]
        log.debug( 'Found URL "%s"' % Url )
        if Url == '':
            self.Path = NoProtocol   # local path
        else:
            self.Path = '/'.join( NoProtocol.split('/')[1:] ) # relative or absolute
        if self.Path == '':
            raise KnownError('Bad URL "%s": missing DIR path!' % LocationExpr)

        return Url

    def _find_logindata(self, Url ):
        # find user data
        try:
            UserPass, HostPort = Url.split('@')
            self.IsRemote = True
        except ValueError:
            self.IsRemote = False
            HostPort = Url
        else: # user is specified
            try:
                self.User, self.Password = UserPass.split('%')
                if self.Protocol in NO_PASSWORD_PROTOCOLS:
                    raise KnownError( 
                        'Passwords are not supported for %s connections' % (
                        ', '.join( [ '"%s"' % proto for proto in NO_PASSWORD_PROTOCOLS] )
                        )
                    )
            except ValueError:
                self.User = UserPass
                self.Password = None
        return HostPort

    def _find_address(self, HostPort ):
        try:
            self.Host, self.Port = HostPort.split(':')
        except ValueError:
            self.Host = HostPort
            self.Port = DEFAULT_PORTS[ self.Protocol ]

        # validate port
        try:
            self.Port = int(self.Port)
            if self.Port < 1 or self.Port > 65535:
                raise ValueError
        except ValueError:
            raise KnownError(
                'Bad port specification "%s" in location "%s". Expecting '
                'integer in range 1 ... 65535' % (self.Port, LocationExpr) 
            )


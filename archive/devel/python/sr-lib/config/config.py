#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HISTORY
    2010-08-24 * rewrite, split up Config into ConfigFile and ConfigText
               * uses ConfigObj Exception __doc__strings for help

"""

__version__ = "$Revision: 0.2.2010-08-24 $"
# $Source$

__all__= [ 
    'Config'            ,
    'ConfigFile'        ,
    'ConfigText'        ,
    'ConfigDefaultText'  ,
    'ConfigError'       , 
    'ConfigFileError'   ,
    'ConfigTextError'   ,
    'ConfigFormatError' ,
]

#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------
# standard    
import os  # write config test to os.devnull() later

# extra modules
from configobj import *
import pt.data.data

# constants, default values

# logging
import logging
log = logging.getLogger( __name__ )

# constants
INTRO = """##############################################################################
#                                                                            #
# CONFIG FILE SYNTAX                                                         #
#                                                                            #
# * continue long lines via '\'                                              #
# * create lists by comma - separating items                                 #
# * boolean var's: False = 0, false, no, off and True  = 1, true, yes, on    #
# * comments: # ; or /* long comments */                                     #
# * sections:                                                                #
#    [section1] [[subsection1]]                                              #
#    reference values of same section or of [DEFAULT] section via ${option}  #
#    names of sections or keys are case-insensitiv                           #
#                                                                            #
##############################################################################
"""



# error class 
#----------------------------------------------------------------------------
class ConfigError(BaseException):
    """General config handling error"""
class ConfigFileError(ConfigError):
    """File handling error"""
class ConfigTextError(ConfigError):
    """Text handling Error"""
class ConfigFormatError(ConfigError):
    """Config content or format errors"""

#-----------------------------------------------------------------------------
# main class
#-----------------------------------------------------------------------------
class Config(ConfigObj):
    """
    DESCRIPTION

    Wrapper for configObj, setting some useful default options. This class 
    is meant to be subclassed by 

    * config file handler class ConfigFile 
    * config text handler class ConfigText

    which do some special checking when initializing. See __doc__ string 
    there. This class can be used as-is but then no file or text content
    checking is done.

    FEATURES
        * read config files formated as of RFC 822
        * comments: # ; or /* long comments */
        * continue long lines via '\'
        * lists are comma separated
          name = value0, value1, value2
        * names of sections or keys are case-insensitiv
        * keywords, values, section names can be surrounded by single or double quotes
        * sections: [section1] [[subsection1]]
          each section can have a [DEFAULT] section, options in
          default section are known to all other sections, too
        * reference values of same section or of DEFAULT section via ${option}
        * boolean variables accept False = 0, false, no, off 
          and True  = 1, true, yes, on

    PARAMETERS
        source       * file or array of config file lines or dictionary or None
        create_empty * True = create new file if not exist, False for array
        file_error   * True = raise on file-not-found, False for array

    METHODS
        reset()     * zero out config data
        merge()     * merge other config obj(in "()" ) with config instance
    """
    def __init__( self, source=None, create_empty=False, file_error=True ):

        if source is None:
            log.debug( "Creating empty config object" ) 
        elif type(source) == type( [] ) or type(source) == type( {} ):
            log.debug( "Creating config object from array or dictionary" ) 
        elif type(source) == type( "" ):
            log.debug( "Creating config object of file '%s'" % source ) 
        else:
            raise ConfigError(
                "Could not initalize ConfigObj, source should be None, "
                "a text array or a filename"
            )

        # initiate parent class
        ConfigObj.__init__( self,
            source                  , 
            create_empty  = create_empty,
            encoding      = 'utf8'      , # yes
            list_values   = True        , # allow comma sep. lists
            file_error    = file_error  , 
            interpolation = 'template'  , # resolve $xx references
            raise_errors  = True        , # raise errors immediately
            stringify     = True        , # do type conversion to strings before writing out
            write_empty_values = True   , # see configobj documentation
        )
        try:
            # next lines are ugly, but found no other way:
            # integrity of config data seems to be testet  only when calling 
            # "print self.items" or write call like below ... otherwise,
            # no exceptions get thrown at errors

            fh = open(os.devnull, 'w')
            fh.write( "%s" % self.items() )
            fh.close()
        except NestingError, emsg:
            raise ConfigFormatError(
                "Mismatch of brackets in section marker\n%s" % emsg
            )
        except ParseError, emsg:
            raise ConfigFormatError( "%s\n%s" % (ParseError.__doc__, emsg) )
        except ReloadError, emsg:
            raise ConfigFormatError( "%s\n%s" % (ReloadError.__doc__, emsg))
        except DuplicateError, emsg:
            raise ConfigFormatError( "%s\n%s" % (DuplicateError.__doc__, emsg) )
        except ConfigspecError, emsg:
            raise ConfigFormatError( "%s\n%s" % (ConfigSpecError.__doc__, emsg) )
        except InterpolationLoopError, emsg:
            raise ConfigFormatError( "Could not replace placeholder, %s" % emsg )
        except MissingInterpolationOption, emsg:
            raise ConfigFormatError( "Could not replace placeholder, %s" % emsg )
        except InterpolationError, emsg:
            raise ConfigFormatError(  "Could not replace placeholder %s" % emsg )
        except RepeatSectionError, emsg:
            raise ConfigFormatError( "Found %s" % emsg )
        except ConfigObjError, emsg:
            raise ConfigFormatError( emsg) 

        # keep old method name for script compatibility
        self.switchFile = self.write_file

    def write_file(self, file_name):
        """ Store config to (other) file.  """

        if self.filename:
            # config file already exists
            log.debug( 
                "Switching config file from '%s' to '%s'"
                % ( self.filename, file_name )
            )
        else: 
            # config file was never written
            log.debug( "Storing config to '%s'" % file_name )

        self.filename = file_name
        try:
            self.write()
        except IOError, emsg:
            if emsg[0] == 2:
                # directory does not exist
                import pt.files.dir
                dir_name = os.path.dirname(file_name )
                try:
                    pt.files.dir.create( dir_name )
                except pt.files.dir.FsDirError, emsg:
                    raise ConfigFileError( 
                        "Could not write to config file '%s':\n%s" 
                        % (file_name, emsg)
                    )

class ConfigFile(Config):
    """
    Initialize configObj config file for reading and writing. See Config()
    __doc__ string.

    PARAMETERS
        source  * config file path
        create_empty * True = create new file if not exist
        file_error   * True = raise on file-not-found

    METHODS

    reload()   * reload config file contents
    write()    * write (changed) config contents to config file
    switchFile()   * store current config to a different path, go on with new path
    """
    def __init__( self, source=None, create_empty=True, file_error=False ):

        # store settings for reuse in reload()
        self.source         = source
        self.create_empty   = create_empty
        self.file_error     = file_error

        self.load()

    def load(self):
        """(re) load config file contents from file"""

        if self.source is None:
            raise ConfigFileError(
                "Specify config file path when calling ConfigFile()!"
            )
   
        try:
            Config.__init__( self, 
                self.source, 
                create_empty = self.create_empty, 
                file_error   = self.file_error,
            )
        except IOError, emsg:
            raise ConfigFileError(
                "Could not  open config file '%s'\n%s" % ( self.source, emsg )
            )

class ConfigText(Config):
    """
    Initialize configObj config object with text variable (or array of config
    file lines) as config source. See Config() __doc__ string.

    METHODS

    reload()        * reload config contents from stored text or array
    write(filename) * write text contents to file
    """
    def __init__( self, content=None ):

        if content is None:
            raise ConfigTextError(
                "Specify config text or array when calling ConfigText()!"
            )


        if type( content ) == type( "" ):
            # convert text to array
            self.content_array = pt.data.data.text2list( content )
        elif type( content ) == type( [] ):
            self.content_array = content
        elif type( content ) == type( {} ):
            self.content_array = False
        else:
            raise ConfigError(
                "Cannot handle content type '%s', try string, "
                "array or dictionary!" % type( content )
            )

        #print '\n'.join(content)
            
        Config.__init__( self,
            self.content_array and self.content_array or content , 
            create_empty  = False ,
            file_error    = False , 
        )

class ConfigDefaultText(ConfigText):
    """
    Initalize config object from text variable with content in the form

    --
    [Target]
    # path: Local backup target containing different mirrors
    # user: User to run backup as. This user should have passwordless
    #       access to given remote source machine.
    # auto: target dir and user are defined by pointing the bp script to
    # the target directory directly. Specify this parameters for exceptions
    # Default:
    #path = auto
    #user = auto
    --

    This text will be converted to a config file with all default values set.
    default values are marked by "#" followed by key name directly.

    Alternatively, text may be given as array of single lines.
    """
    def __init__(self, content ):
        """Uncomment all default values from config content"""
        # regexp class
        import re
        
        # convert text to array anyway 
        if   type(content) == type(""):
            raw_lines    = pt.data.data.text2list( content )
        elif type(content) == type([]):
            raw_lines    = content
        else: 
            raise ConfigError(
                "Data type '%s' for input is not supportet" % type(content)
            )

        re_pattern = r"""
        ^\s*                   # start of line, followed by optional whitespaces
        \#                     # "#" ...
            (
               [A-Za-z0-9_][^=]*      # ... followed by option directly 
                               # (no spaces after "#")  
                \s* = .*           # whitespace, =, any characters
            )
        $ # end of line
        """

        re_pattern_compiled = re.compile( re_pattern, re.VERBOSE )
        lines = [ re_pattern_compiled.sub( "\\1", line ) for line in raw_lines    ]

        # hand over array with uncommented default options to text config handler
        ConfigText.__init__(self, lines )


if __name__ == "__main__":
    from pt.logger import *
    log = Logger(
            level        = logging.DEBUG,
            file_file    = None,      # None = no file logging
            file_level   = logging.INFO,
        )



# #   print text
#    cfg = ConfigFile( "/etc/backup/backup.conf" )
#    print cfg.items()
#    cfg.write_file( "/etc/backup/backup.conf2" )
#    ct.switchFile("/tmp/delme")
#    print ct['Daemon']['id']
#    ct['kuul'] = 'j schaunsqdwedwederfefr'
#    ct.write()
#
#    cf = ConfigFile('/tmp/delmex')
#    cf.merge(ct)
#    cf.write()

    test_default_config = """
[Source]
# path: Source dir/file on local or remove machine
# host: If given, source is remote an acessed via ssh
# user: Remote ssh user
# port: Remote ssh port
# Default:
#path =
#host =
#user eferg ege = root
#port = 22
    """

    def_cfg = ConfigDefaultText( test_default_config )
    def_cfg.write_file("test-delme")









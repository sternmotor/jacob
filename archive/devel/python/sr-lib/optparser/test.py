#!/usr/bin/env python


from optparser import OptParser, OptParserError



# define option parser
parser = OptParser(
    usage = (
        '%prog CMD PATH'
        '\nwhere CMD is one of create, touch or remove'
    ),
    description = 'advanced directory handler'   ,
)
    
parser.add_option( '-t', '--target', dest="target",
                action='store_true', default = False,
                help='destination')
     



opts,args = parser.parse_args( [ "-h" ])

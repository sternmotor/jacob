import fnmatch
import argparse

def parser_add_include(Parser, ValidIncludes, ObjectName ):

    Parser.add_argument('-i', '--include', action='append', required=False,
        default=[], help="""
            Specify %ss to operate on. All other %ss and those specified by 
            "--exclude ..." are omitted.
            In case no "--include ..." or "--include *" is specified, 
            all %ss are processed.            
            For including multiple %ss, use unix shell-style wildcards 
            (*, ?, [seq], [!seq]) or repeat "--include ..." as often as needed.
            Valid "--include" choices are (eventually wildcarded): %s.
        """ %  ( 
            ObjectName, ObjectName, ObjectName, ObjectName, 
            ', '.join(ValidIncludes),
        )
    )

def parser_add_exclude(Parser, ValidExcludes, ObjectName ):
    Parser.add_argument('-e', '--exclude', action='append', required=False, 
        default=[], help="""
            Specify %ss to exclude from processing, narrowing "--include ..."  
            options (respectively selection of all %ss in case no "--include 
            ..." is given). For excluding multiple %ss, use unix shell-style 
            wildcards (*, ?, [seq], [!seq]) or repeat "--include ..." as often 
            as needed. Valid "--exclude" choices are (evtl. wildcarded): %s.
        """ % (    
            ObjectName, ObjectName, ObjectName, ', '.join(ValidExcludes),
        )
    )

def fix_include_logic( All, Includes=[], Excludes=[]):
    """
    Take all available objects, select includes (by wildcard) and 
    substract excludes (by wildcard)

    excludes override/narrow include selection.

    in case includes= [] or *: all objects selected
    in case excludes= [] or *: no objects removed (return all included objects )

    fnmatch provides support for Unix shell-style wildcards
    """

    # run through include definitions
    if Includes == []:
        FilteredIncludes = list(All)
        log.debug( 'Empty include definition - added All objects to includes list' )
    else:
        # apply include filter to All
        FilteredIncludes = []
        for IncludeExpression in Includes:
            NewObjects = fnmatch.filter(All, IncludeExpression) 
            # add matching objects
            if NewObjects:
                FilteredIncludes.extend( NewObjects )
                log.debug( 
                    'Added --include "%s" matches: %s' % ( 
                        IncludeExpression, ', '.join(NewObjects)
                    )
                )

    # substract excludes from included objects
    UniqIncludesSet = set( uniq( FilteredIncludes ) )
    for ExcludeExpression in Excludes:
        ExcessObjects = fnmatch.filter( UniqIncludesSet, ExcludeExpression)
        # remove matching objects
        if ExcessObjects:
            UniqIncludesSet = UniqIncludesSet - set(ExcessObjects)
            log.debug( 
                'Removed --exclude "%s" matches: %s' % ( 
                    ExcludeExpression, ', '.join(ExcessObjects)
                )
            )

    # return filtered objects
    FinalObjects = sorted( list ( UniqIncludesSet ) )
    log.debug(
        'Processing following objects: %s' % (', '.join(FinalObjects))
    )
    return FinalObjects

def uniq(alist):    # Fastest, does order preserving
    """Remove duplicates from alist"""
    set = {}
    return [set.setdefault(e,e) for e in alist if e not in set]

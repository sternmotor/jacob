#!/usr/bin/env python
"""
Strip config files or other files from comments( /**/ or # style),
empty lines and join lines concentated by '\'

Usage example1:

    fh = open('/etc/fstab', 'r')
    print =  strip_text( fh.readlines())
    fh.close


Usage example2:
	print strip_file('/etc/fstab' )
"""


__ALL__ = [ 'strip_file', 'strip_text'   ]

import re

def _strip_c_comments( text_string ):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
    """

    pattern = r"""
                            ##  --------- COMMENT ---------
           /\*              ##  Start of /* ... */ comment
           [^*]*\*+         ##  Non-* followed by 1-or-more *'s
           (                ##
             [^/*][^*]*\*+  ##
           )*               ##  0-or-more things which don't start with /
                            ##    but do end with '*'
           /                ##  End of /* ... */ comment
         |                  ##  -OR-  various things which aren't comments:
           (                ## 
                            ##  ------ " ... " STRING ------
             "              ##  Start of " ... " string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^"\\]       ##  Non "\ characters
             )*             ##
             "              ##  End of " ... " string
           |                ##  -OR-
                            ##
                            ##  ------ ' ... ' STRING ------
             '              ##  Start of ' ... ' string
             (              ##
               \\.          ##  Escaped char
             |              ##  -OR-
               [^'\\]       ##  Non '\ characters
             )*             ##
             '              ##  End of ' ... ' string
           |                ##  -OR-
                            ##
                            ##  ------ ANYTHING ELSE -------
             .              ##  Anything other char
             [^/"'\\]*      ##  Chars which doesn't start a comment, string
           )                ##    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text_string) if m.group(2)]

    return "".join(noncomments)

def _join_lines( text):

    new_text = []
    joined_line = ''
    for line in text:
        if line.endswith('\\'):
            joined_line += line.strip('\\')
            continue
        else:
            if joined_line:
                new_text.append( joined_line + line )
                joined_line = ''
            else:
                new_text.append( line )
             
    return new_text

def from_text( text ):
    """ 
    Filter text array : remove comments and empty lines
    Order of strips here is important!
    """

    # 1.  strip c comments
    text_string = '\n'.join(text)
    no_c = _strip_c_comments( text_string )
    no_c_text = no_c.split('\n')    

    # 2. strip # comments
    stripped_text = []
    for line in no_c_text:
        new_line = line.split('#')[0].strip()
        if new_line: 
            stripped_text.append(new_line)

    # 3. join lines
    return _join_lines( stripped_text )



def from_file( file_name ):
    """ 
    Filter file, see strip_text
    """

    fh = open( file_name, 'r')
    unstripped = fh.readlines() 
    fh.close()
    return from_text( unstripped )

if __name__ == '__main__':

    print from_file( '/etc/fstab')
    print

    fh = open('/etc/fstab', 'r')
    stripped =  from_text( fh.readlines())
    fh.close

    print "XX\n".join(stripped)


#!/usr/bin/env python
"""
Read a dhcpd.conf/ nginx.conf/ drbd.conf style config into dictionary
Main function: 
get_config( <file name>)

returns dictionary
"""


import pt.files.strip

LINE_BREAK_CHARS = ('{', '}', ';' )

def break_text( text ):
    broken_line = ''
    new_text = []
    for line in text:
        for char in line:
            for break_char in LINE_BREAK_CHARS:
                if char == break_char:
                    broken_line += char
                    new_text.append( broken_line.strip() )
                    broken_line = ''
                    break;
            else:
                broken_line += char
    return new_text
    
def read_section( text ):
    """
    Recursively scan sections and parameters in lines 
    input: array containing config file lines
    output_ dictionary containing data
    """

    # current section's sub sections and parameters
    section = {}
    # starting scope: current section
    scope = 'local'
    # array for sub section's lines
    subsection_lines = []
    # 1 + for incoming '{' markers 
    openbrackets_counter = 0

    for line in text:
        # new parameter
        if   line.endswith( ';' ): 
            if scope == 'local' : 
                parameter = line.strip(';')
                try:
                    section['parameters'].append ( parameter )
                except KeyError:
                    section['parameters'] = [ parameter ]
                continue

            elif scope == 'subsection':
                subsection_lines.append( line )
        # new section: store name an let loop collect all lines
        elif line.endswith('{') and scope == 'local':
            # look for matching bracked
            scope = 'subsection'
            subsection_name = line.strip('{').strip()
            continue

        # in subsection
        elif line.endswith('{') and scope == 'subsection':
            openbrackets_counter += 1
            subsection_lines.append( line )

        # some bad condition 
        elif line.endswith('}'):

            if   scope == 'local':
                raise BaseException( 
                    "Found closing bracket but no opening bracket after lines \n%s\n%s"
                    % (line, '\n'.join( subsection_lines) )
                )

            elif scope == 'subsection':

                if openbrackets_counter == 0:
                    # finished collectin new section's data
                    subsection_lines.append( line.strip('}').strip() )

                    subsection =  read_section( subsection_lines ) 
                    section[ subsection_name ] =  subsection 

                    scope = 'local'
                    subsection_lines = []
                else:
                    # still in section
                    subsection_lines.append( line )
                    openbrackets_counter -= 1

    # end of lines: end of local section
    return section


def get_config( file_name ):
    """ 
    Can be changed to pt.files.strip_file.strip_text
    """

    # read file
    stripped_text = pt.files.strip.from_file( file_name )

    # break lines
    broken_text  = break_text( stripped_text )

    # read data
    return read_section( broken_text)


if __name__ == '__main__':
    import pprint

    FILE = 'config_drbd_style.test.conf'

    pprint.pprint( get_config(FILE) )


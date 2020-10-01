Python data handling
====================





Convert a dictionary to class allow calling like xxx.yyy instead of xxx['yyy']

    class dict2class():
        """store params dict as class allowing simple access notation args.<key>"""

        def __init__(self, dictionary):
             for key in dictionary:
                 setattr(self, key, dictionary[key])






====== Python Scripting ======
===== Script Template =====
===== Style Guide and HowTo's =====

==== Script Structures, Error Handling ====



=== Exception Class ===

  * allways inherit from Exception base class
  * define Exception:<code>
class ShellError(Exception):
    pass
class ShellSystemError(ShellError):
    """Errors calling system commands""" 
    def __init__(self, cmd, msg, ecode):
        self.cmd    = cmd              
        self.msg    = msg             
        self.ecode  = ecode   
        ShellError.__init__(self, msg)
</code>

   * raise exception like:<code>
raise ShellSystemError(  
    err.cmd,
    "Bad exit code %s for system command!" % err.returncode , 
    err.returncode,
)
</code>


  * catch and usage exception like:<code>                                                                                           
try:
    shell.system('ls -lt --badOPTION')
except ShellSystemError, err:  
    print err.ecode                    
    print err.cmd 
</code>



==== Data Structures and Logic, Math ====
==== Text Files, Unicode, Strings and Regexp ====
=== Regular Expressions ===

  * always use raw strings (r'' or r"") to contain patterns
  * re.search() behaves like Perl's  <nowiki>m//</nowiki>, avoid using re.match()
  * groups() method returns all matches as a tuple
  * replace all instances of a pattern: re.sub(), limit to 1 ... 2nd match by "max" parameter
  * make the regular expression match case-insensitive: add (?i) to the beginning of the expression
==== Filesystem, Date, Time ====
=== Handling Files and Folders ===
  * open files and make sure this file is getting closed as soon as possible: <code>
with open("myfile.txt") as f:
    for line in f:
        print line,
</code>
==== Config and Command Line Options ====
==== Logging, Mail and Messages ====
==== System Command Execution ====
==== Daemon, Threads, Parallel Processing ====
==== Databases, Net, RPC, Users, Groups ====



===== Fehlersuche, Debugging  =====

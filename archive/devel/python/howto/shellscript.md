
## run system commands

### use subprocess

### replace by native python commands

## system
* os.chroot(path)
* os.devnull
* os.env['HOME', DEFAULT_HOME]
* os.get_terminal_size()
* os.getuid()
* os.kill(pid, sig) # -see signal module
* os.linesep
* os.nice			# process nice level
* os.strerror(Index) #  see https://docs.python.org/2/library/os.html, last quarter of text
* os.waitpid(pid,0)  # pid = 0: wait for any child process of current process 
* os.walk(path)
* shutil.which(cmd) # none if not found

## path manipulation
* os.path.basename(path)  # path > $pathname, basename > $name
* os.path.commonprefix(list)
* os.path.dirname(path)   # path > $pathname, dirname  > $path
* os.path.exists(path) 
* os.path.getmtime(path) # modification date of file
* os.path.isdir(path): true:exists and is directory
* os.path.isfile(path) true: file or link
* os.path.join(list)
* os.path.realpath(path) : physical path, symlinks resolved
* os.path.split(path) : segments of path

## files
* os.access(path, os.F_OK os.R_OK os.W_OK os.X_OK)
* os.chmod(path, mode)  # mod in python3: 0o750
* os.fstat(fd)	# file info
* os.link(source, link_name)	# hard link
* os.makedirs(path, exist_ok=True) # recursive directory creation, simple is os.mkdir(path)
* os.readlink(path) # read source for Link_name
* os.remove(path) = os.unlink(path)
* os.symlink(source, link_name) # symbolic link
* shutil.chown(path, user, group)	
* shutil.copy	# copy data and permission, ignore mode (use copy2 then)
* shutil.copytree(symlinks=True) # copy tree recursively, dst must not exist
* shutil.move(src, dst) # uses os.rename() if same fielsystem, otherwise copy + delete
* shutil.rmtree(path)
* tempfile.TemporaryDirectory(prefix=None, suffix=None) # unsecure, self-destroying
* tempfile.TemporaryFile(prefix=None, suffix=None) # unsecure, self-destroying
* tempfile.mkstemp(suffix='.secure', prefix=None, dir='basedir')		# secure, must be removed "manually"
* tempfile.mkdtemp(suffix='.secure', prefix=None, dir='basedir')		# secure, must be removed "manually"

## file system
* glob.glob('/etc/filena*')
* os.chdir(path)
* os.curdir # '.'
* os.fstatvfs(fd)  # file system info where fd resides
* os.getcwd()
* os.pardir # current parent directory ('..')
* shutil.diskusage(path) # du, total/used/free

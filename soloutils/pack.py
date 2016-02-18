"""
Creates a tarball containing a script to run and its environment
"""

import os
import shutil
import sys
import tempfile
import virtualenv
import subprocess
import tarfile
 
def is_win():
    return (sys.platform == 'win32')
    
def spew_string_to_filepath(string, filepath):
    fd = open(filepath, "w")
    fd.write(string)
    fd.close()
    
def spew_string_to_tmpscript(string):
    '''Write a string out to a file which can then be executed'''
    if is_win():
        mysuffix = ".bat"
    else:
        mysuffix = ""

    tmp = tempfile.NamedTemporaryFile(mode='w+b', delete=False,suffix=mysuffix)
    if not is_win():
        os.chmod(tmp.name, 0700)
    tmp.write(string)
    tmp.close()

    return tmp.name

def write_distutils_pth(outfilepath):
    content = '''import sys; import distutils.core; s = distutils.core.setup; distutils.core.setup = (lambda s: (lambda **kwargs: (kwargs.__setitem__("ext_modules", []), s(**kwargs))))(s)'''
    spew_string_to_filepath(content, outfilepath)

def run_in_env(basedir, command):
    '''run command in the created environment'''
    # write out a batch script
    if is_win():
        source = ""
        activate = "env\\bin\\activate.bat"
        shebang = ""
    else:
        source = "source"
        activate = "env/bin/activate"
        shebang = "#!/bin/bash"

    content = '''{shebang}

cd "{basedir}"
{source} {activate}
{command}
'''.format(command=command,
           basedir=basedir,
           activate=activate,
           source=source,
           shebang=shebang)

    path = spew_string_to_tmpscript(content)
    print("script is at %s" % (path,))

    # run the script...
    subprocess.call(path)

def excludefn(contentdir, filename):
    '''Returns True if filename should be excluded from archive'''
#    print("filename: %s" % filename)
    for part in [".git", "env", "solo-script.tar.gz"]:
        fullpath = os.path.join(contentdir, part)
        if filename.startswith(fullpath):
            return True

    return False

def find_site_packages_directory(startdir):
    for dirpath, dirnames, filenames in os.walk(startdir):
        if "site-packages" in dirnames:
            return os.path.join(dirpath, "site-packages")
    raise Exception("site-packages not found in (%s)" % (startdir,))

def main(args):
    print 'Creating script archive...'

    # use a temporary directory to hold a copy of the content to be archived:
    tmpdir = tempfile.mkdtemp()

    # remove old contents of temporary directory:
    if tmpdir is None:
        print("tmpdir is None")
        abort()
        #    shutil.rmtree(tmpdir)
    
    # copy the script and its libraries into a subdirectory of tmpdir:
    contentdir = os.path.join(tmpdir, "content")
    shutil.copytree(".", contentdir)

    # remove any old environment that might have been present in source:
    envdir = os.path.join(contentdir, "env")
    try:
        shutil.rmtree(envdir)
    except OSError as e:
        if e.errno != 2:
            raise e

    # create new virtual environment:
    virtualenv.create_environment(envdir)

    site_packages_directory = find_site_packages_directory(envdir)
    # write out a configuration script:
    print("site packages directory: %s" % (site_packages_directory,))
    write_distutils_pth(os.path.join(site_packages_directory, 'distutils.pth'))

    run_in_env(contentdir, "pip install wheel")
    run_in_env(contentdir, "pip wheel -r requirements.txt -w wheelhouse")

    tarball_name = "solo-script.tar.gz"
    print("Creating tarball (%s)" % tarball_name)
    tarball = tarfile.open(name=tarball_name, mode="w:gz")
    tarball.add(contentdir,
                recursive=True,
                arcname=".",
                exclude=lambda x : excludefn(contentdir, x))
    tarball.close()

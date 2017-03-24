# 
# setup script for pycbc_glue

import os, sys, shutil
import subprocess
import time

try:
  from sys import version_info
except:
  print >> sys.stderr, "Unable to determine the python version"
  print >> sys.stderr, "Please check that your python version is >= 2.6"
  sys.exit(1)

if version_info < (2, 6):
  print >> sys.stderr, "Your python version " + str(version_info) + " appears to be less than 2.6"
  print >> sys.stderr, "Please check that your python version is >= 2.6"
  print >> sys.stderr, "Glue requires at least version 2.6"
  sys.exit(1)

try:
    from setuptools import setup
    from setuptools.command import install
except ImportError as e:
    if os.path.basename(os.path.dirname(__file__)).startswith('pip-'):
        e.args = ('setuptools module not found, cannot proceed with pip '
                  'install',)
        raise
    from distutils.core import setup
    from distutils.command import install
    
from distutils.core import Extension
from distutils.command import build_py
from distutils.errors import DistutilsError
from distutils.command import sdist
from distutils.command import clean
from distutils.file_util import write_file
from distutils import log

from misc import generate_vcs_info as gvcsi

class glue_install(install.install):
    def run(self):
        etcdirectory = os.path.join(self.install_data, 'etc')
        if not os.path.exists(etcdirectory):
            os.makedirs(etcdirectory)

        filename = os.path.join(etcdirectory, 'pycbc_glue-user-env.sh')
        self.execute(write_file,
                     (filename, [self.extra_dirs]),
                     "creating %s" % filename)

        env_file = open(filename, 'w')
        print >> env_file, "PATH=" + self.install_scripts + ":$PATH"
        print >> env_file, "PYTHONPATH=" + self.install_libbase + ":$PYTHONPATH"
        print >> env_file, "export PYTHONPATH"
        print >> env_file, "export PATH"
        env_file.close()

        #try:
        #    install.install.do_egg_install(self)
        #except DistutilsError as err:
        #    print err
        #else:
        install.install.run(self)

def write_build_info():
    """
    Get VCS info from pycbc_glue/generate_vcs_info.py and add build information.
    Substitute these into pycbc_glue/git_version.py.in to produce
    pycbc_glue/git_version.py.
    """
    date = branch = tag = author = committer = status = builder_name = build_date = ""
    id = "1.1.0"
    
    try:
        v = gvcsi.generate_git_version_info()
        id, date, branch, tag, author = v.id, v.date, b.branch, v.tag, v.author
        committer, status = v.committer, v.status

        # determine current time and treat it as the build time
        build_date = time.strftime('%Y-%m-%d %H:%M:%S +0000', time.gmtime())

        # determine builder
        retcode, builder_name = gvcsi.call_out(('git', 'config', 'user.name'))
        if retcode:
            builder_name = "Unknown User"
        retcode, builder_email = gvcsi.call_out(('git', 'config', 'user.email'))
        if retcode:
            builder_email = ""
        builder = "%s <%s>" % (builder_name, builder_email)
    except:
        pass

    sed_cmd = ('sed',
        '-e', 's/@ID@/%s/' % id,
        '-e', 's/@DATE@/%s/' % date,
        '-e', 's/@BRANCH@/%s/' % branch,
        '-e', 's/@TAG@/%s/' % tag,
        '-e', 's/@AUTHOR@/%s/' % author,
        '-e', 's/@COMMITTER@/%s/' % committer,
        '-e', 's/@STATUS@/%s/' % status,
        '-e', 's/@BUILDER@/%s/' % builder_name,
        '-e', 's/@BUILD_DATE@/%s/' % build_date,
        'misc/git_version.py.in')

    # FIXME: subprocess.check_call becomes available in Python 2.5
    sed_retcode = subprocess.call(sed_cmd,
        stdout=open('pycbc_glue/git_version.py', 'w'))
    if sed_retcode:
        raise gvcsi.GitInvocationError
    return id

ver = write_build_info()


setup(
  name = "pycbc-glue-obsolete",
  version = ver,
  author = "Duncan Brown",
  author_email = "duncan.brown@ligo.org",
  description = "Grid LSC User Engine",
  url = "https://github.com/ligo-cbc/pycbc-glue",
  download_url = "https://github.com/ligo-cbc/pycbc-glue/archive/v1.1.0.tar.gz",
  license = 'See file LICENSE',
  packages = [ 'pycbc_glue', 'pycbc_glue.ligolw', 'pycbc_glue.ligolw.utils', 'pycbc_glue.segmentdb', 'pycbc_glue.auth'],
  cmdclass = {'install' : glue_install,},
  ext_modules = [
    Extension(
      "pycbc_glue.ligolw.tokenizer",
      [
        "pycbc_glue/ligolw/tokenizer.c",
        "pycbc_glue/ligolw/tokenizer.Tokenizer.c",
        "pycbc_glue/ligolw/tokenizer.RowBuilder.c",
        "pycbc_glue/ligolw/tokenizer.RowDumper.c"
      ],
      include_dirs = [ "pycbc_glue/ligolw" ]
    ),
    Extension(
      "pycbc_glue.ligolw._ilwd",
      [
        "pycbc_glue/ligolw/ilwd.c"
      ],
      include_dirs = [ "pycbc_glue/ligolw" ]
    ),
    Extension(
      "pycbc_glue.__segments",
      [
        "src/segments/segments.c",
        "src/segments/infinity.c",
        "src/segments/segment.c",
        "src/segments/segmentlist.c"
      ],
      include_dirs = [ "src/segments" ]
    )
  ],
  scripts = [
    os.path.join('bin','ligolw_add'),
    os.path.join('bin','ligolw_combine_segments'),
    os.path.join('bin','ligolw_cut'),
    os.path.join('bin','ligolw_print'),
    os.path.join('bin','ligolw_print_tables'),
    os.path.join('bin','ligolw_segment_diff'),
    os.path.join('bin','ligolw_segment_intersect'),
    os.path.join('bin','ligolw_segment_query'),
    os.path.join('bin','ligolw_segment_union'),
    os.path.join('bin','ligolw_segments_from_cats'),
    os.path.join('bin','ligolw_diff'),
    ],
  data_files = [
    ( 'etc', [ 
        os.path.join('etc','ligolw.xsl'),
        os.path.join('etc','ligolw.js'),
        os.path.join('etc','ligolw_dtd.txt') 
      ]
    )
  ]
)

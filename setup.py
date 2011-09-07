import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.0',
    'SQLAlchemy',
    'transaction',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'zope.sqlalchemy',
    'WebError',
    'WebHelpers>=1.3',
    'simplejson>=2.1.5',
    'decorator>=3.2.0',
    'Chameleon>=2.0-rc11',
    'httplib2>=0.6.0',
    'python-twitter>=0.8.2',
    'pysqlite',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='my-forms',
      version='0.0',
      description='my-forms',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='myforms',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = myforms:main
      """,
      paster_plugins=['pyramid'],
      )

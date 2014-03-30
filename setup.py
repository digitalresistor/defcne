import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.5b1',
    'SQLAlchemy',
    'psycopg2',
    'transaction',
    'pyramid_tm',
    'zope.sqlalchemy',
    'waitress',
    'cryptacular',
    'misaka',
    'deform',
    'deform_bootstrap',
    'pyramid_deform',
    'pyramid_mailer',
    'pyramid_mako',
    ]

development = requires + [
    'pyramid_debugtoolbar',
    ]

setup(name='defcne',
      version='0.0.5',
      description='defcne',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Bert JW Regeer',
      author_email='bertjw@regeer.org',
      url='http://defcne.net/',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='defcne',
      install_requires=requires,
      extras_require = {
          'develop': development
          },
      entry_points="""\
      [paste.app_factory]
      main = defcne:main
      [console_scripts]
      defcne_create_db = defcne.scripts.initializedb:main
      defcne_destroy_db = defcne.scripts.destroydb:main
      """,
      )

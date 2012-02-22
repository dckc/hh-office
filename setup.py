from setuptools import setup, find_packages

setup(name='hh-office',
      version='0.1a',
      description='office app migration tools',
      author='Dan Connolly',
      author_email='dckc@madmode.com',
      url='http://www.madmode.com/',
      packages=find_packages(),
      install_requires=[
          'SQLAlchemy>=0.7',
          'MySQL-python',
          'mechanize',
          'paste'
          # Paste-1.7.5.1.tar.gz#md5=7ea5fabed7dca48eb46dc613c4b6c4ed
          # ClientForm-0.2.10-py2.6.egg#md5=86f1cca840d245e2612cc558492f5eb3
    ])

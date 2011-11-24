from setuptools import setup, find_packages

setup(name='hh-office-claims',
      version='0.1a',
      description='Medical Claim Tools',
      author='Dan Connolly',
      author_email='dckc@madmode.com',
      url='http://www.madmode.com/',
      packages=find_packages(),
      install_requires=[
          'xlrd',
          # tested with
          # xlrd-0.7.1.zip#md5=851bd20873224d97cfb5ccca2d22b81c
          'sqlalchemy'
          ])

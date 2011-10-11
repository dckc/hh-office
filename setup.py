from setuptools import setup, find_packages

setup(name='hh-office',
      version='0.1a',
      description='office app migration tools',
      author='Dan Connolly',
      author_email='dckc@madmode.com',
      url='http://www.madmode.com/',
      packages=find_packages(),
      install_requires=[
    'SQLAlchemy>=0.7'
    ])

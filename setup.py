from setuptools import setup, find_packages

setup(
    name='dirsync',
    version='0.1',
    description='Keep directories in sync over a network',
    author='Grahame Gardiner',
    author_email='grahamegee@gmail.com',
    url='https://github.com/grahamegee/dirsync',
    install_requires=[
        'asyncio'
    ],
    extras_require={}
)

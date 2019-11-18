from setuptools import setup
from anyencoder import __title__, __version__


with open('README.rst') as file:
    readme = file.read()

setup(
    name=__title__,
    version=__version__,
    description='Easily juggle multiple object serializers',
    long_description=readme,
    python_requires='>=3.7',
    install_requires=['multi_key_dict'],
    packages=['anyencoder', 'anyencoder.plugins'],
    author='Andrew Blair Schenck',
    author_email='aschenck@gmail.com',
    url='https://www.github.com/andrewschenck/py-anyencoder',
    license='Apache 2.0',
)

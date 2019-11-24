from setuptools import setup


with open('README.rst') as file:
    readme = file.read()


setup(
    name='anyencoder',
    version='0.0.1',
    description='Easily manage multiple object serializers',
    long_description=readme,
    python_requires='>=3.7',
    install_requires=['multi_key_dict >= 2.0.3'],
    packages=['anyencoder', 'anyencoder.plugins'],
    author='Andrew Blair Schenck',
    author_email='aschenck@gmail.com',
    url='https://www.github.com/andrewschenck/py-anyencoder',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache License 2.0',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

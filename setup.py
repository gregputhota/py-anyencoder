from setuptools import setup


with open('README.rst') as file:
    readme = file.read()


setup(
    name='anyencoder',
    version='0.0.3',
    description='Dynamic dispatch for object serialization',
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
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

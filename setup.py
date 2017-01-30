from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='a-mbot',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',

    description='Personal Twitch bot',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/antoniobanderaz/a_mbot',

    # Author details
    author='Alexander Davydov',
    author_email='mrgeneroth@gmail.com',

    # Choose your license
    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',

        'Topic :: Communications :: Chat :: Internet Relay Chat'
    ],

    keywords='twitch irc bot',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),


    install_requires=['beautifulsoup4==4.5.3',
                      'goslate==1.5.1',
                      'gTTS==1.1.8',
                      'pymorphy2==0.8',
                      'requests==2.13.0'],


    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'a_mbot=a_mbot.main:start_loop',
        ],
    },
)

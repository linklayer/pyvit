from setuptools import setup, find_packages

setup(
    name='pyvit',
    version='0.1.1',
    packages=find_packages(),
    scripts=[],

    install_requires=[
        'pyserial>=3.2.1'
    ],

    test_suite='test',

    author='Eric Evenchick',
    author_email='eric@evenchick.com',
    url='http://github.com/linklayer/pyvit',
    license='GPLv3',
    description='Python Vehicle Inteface Toolkit',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 3 - Alpha',
                 ('License :: OSI Approved :: ' +
                  'GNU General Public License v3 (GPLv3)'),
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Embedded Systems']
)

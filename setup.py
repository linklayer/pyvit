from distutils.core import setup

setup(
    name='CANard',
    version='0.2.2',
    author='Eric Evenchick',
    author_email='eric@evenchick.com',
    packages=['canard', 'canard.test', 'canard.hw', 'canard.utils', 'canard.proto'],
    scripts=[],
    url='http://github.com/ericevenchick/CANard',
    license='GPLv3',
    description='Library for interacting with Controller Area Network (CAN)',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 3 - Alpha',
		 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		 'Topic :: Software Development :: Libraries',
		 'Topic :: Software Development :: Embedded Systems']


)

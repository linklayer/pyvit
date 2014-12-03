from distutils.core import setup

setup(
    name='CANard',
    version='0.1-dev',
    author='Eric Evenchick',
    author_email='eric@evenchick.com',
    packages=['canard', 'canard.test', 'canard.hw'],
    scripts=[],
    url='http://pypi.python.org/pypi/CANard/',
    license='LICENSE.txt',
    description='Library for interacting with Controller Area Network (CAN).',
    long_description=open('README.rst').read(),
)

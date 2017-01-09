from setuptools import setup

setup(
    name='axi',
    version='0.1',
    description='Library for working with the AxiDraw v3 pen plotter.',
    author='Michael Fogleman',
    author_email='michael.fogleman@gmail.com',
    packages=['axi'],
    install_requires=['pyserial', 'shapely'],
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
)

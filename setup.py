from distutils.core import setup

setup(
    name='greendo',
    version='0.1',
    packages=['greendo',],
    license='Apache License 2.0',
    long_description='a client library for the RYOBI GDO (Garage Door Opener)',
    install_requires=['websocket-client',],
)

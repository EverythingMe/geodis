from setuptools import setup
setup(name='geodis',
    version='1.0',
    packages=['geodis', 'geodis.provider'],
    scripts=['geodis/geodis'],
    install_requires=['redis>=2.7.1', 'geohasher==0.1dev', 'upoints==0.12.2'],
#   url='https://github.com/EverythingMe/kickass-redis',
    author='Dvir Volk',
    description= 'Geodis - a redis based geo tagging and geo resolving library'
)

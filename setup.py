from setuptools import setup, find_packages

def listify(filename):
    return filter(None, open(filename,'r').read().split('\n'))

setup(
    name = "django-cache-sweeper",
    version = "0.1.2",
    url = 'http://github.com/smn/django-cache-sweeper',
    license = 'BSD',
    description = "Lazy Django fragment cache sweeping",
    long_description = open('README.rst', 'r').read(),
    author = 'Simon de Haan',
    author_email = "simon@praekeltfoundation.org",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = listify('requirements.pip'),
    classifiers = listify('CLASSIFIERS.txt')
)


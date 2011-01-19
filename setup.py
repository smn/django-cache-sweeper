from setuptools import setup, find_packages

setup(
    name = "dango-cache-sweeper",
    version = "0.1",
    url = 'http://github.com/smn/django-cache-sweeper',
    license = 'BSD',
    description = "Lazy Django fragment cache sweeping",
    long_description = open('README.md', 'r').read(),
    author = 'Simon de Haan',
    author_email = "simon@praekeltfoundation.org",
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = map(lambda s: s.strip(), open('requirements.pip','r').readlines()),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)


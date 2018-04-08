# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from django_addons import __version__


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='django-addons',
    version=__version__,
    description='django-addons Framework',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/django-addons/django-addons',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        # Django dependency is intentionally left out as a workaround for pips
        # ignorance regarding exact versions to install.
        # 'Django',
        'django-getenv',
        'django-addons-formlib',
    ],
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
)

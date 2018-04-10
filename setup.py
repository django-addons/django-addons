# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from django_addons import __version__


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
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 2.0',
    ],
)

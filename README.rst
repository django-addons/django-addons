#######################
Django Addons Framework
#######################


|PyPI Version|

`Django Addons`_ are re-usable django apps that follow certain conventions to
abstract out complicated configuration from the individual django website
project into upgradable packages. With this approach it is possible
to avoid repetitive "add this to ``INSTALLED_APPS`` and that to
``MIDDLEWARE_CLASSES`` and add these to ``urls.py``" work. The settings logic
is bundled with the Addon and only interesting "meta" settings are exposed.

``django-addons`` is a framework to utilise such Addons in django projects.

The goal is to keep the footprint inside the django website project as small
as possible, so updating things usually just mean bumping a version in
``requirements.txt`` and no other changes in the project.


======================
Installation & Updates
======================

Add ``django-addons`` to your projects ``requirements.txt`` or pip install it.
It is also highly recommended to install ``django-addon``. This is django
itself bundled as an Addon.
::

    pip install django-addons django-addon


settings.py
===========

At the top if the settings the following code snippet::

    INSTALLED_ADDONS = [
        'django_addons',
        'django_addon',
    ]

    import django_addons.settings
    django_addons.settings.load(locals())

    # add any other custom settings here


urls.py
=======

Addons can automatically add stuff to the root ``urls.py`` so it's necessary
to add ``django_addons.urls.patterns()`` and
``django_addons.urls.i18n_patterns()``.

::

    from django_addon.utils import i18n_patterns
    import django_addons.urls


    urlpatterns = [
        # add your own patterns here
    ] + django_addons.urls.patterns() + i18n_patterns(
        # add your own i18n patterns here
        *django_addons.urls.i18n_patterns()  # MUST be the last entry!
    )


Please follow the installation instructions for django-addon for complete
integration.


Adding Addons
=============

In this example we're going to install `django-celery-addon`_.

pip install the Addon::

    pip install django-celery-addon

Add it to ``INSTALLED_ADDONS`` in ``settings.py``::

    INSTALLED_ADDONS = [
        'django_addons',
        'django_addon',
        'django_celery_addon',
    ]

``django-celery-addon`` comes with a ``addon_config.py`` file, which is
automatically picked up and used to configure celery. Some Addons also
have a ``addon_form.py`` file, which contains a form defining some
"meta-settings" to influence the configuration.


============
Contributing
============

This is a community project. We love to get any feedback in the form of
`issues`_ and `pull requests`_.

.. _issues: https://github.com/django-addons/django-addons/issues
.. _pull requests: https://github.com/django-addons/django-addons/pulls
.. _Django Addons: http://docs.aldryn.com/en/latest/reference/addons/index.html

.. |PyPI Version| image:: http://img.shields.io/pypi/v/django-addons.svg
   :target: https://pypi.python.org/pypi/django-addons

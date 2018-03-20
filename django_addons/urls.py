# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import include, path


def patterns():
    pats = [
        path('', include(url))
        for url in getattr(settings, 'ADDON_URLS', [])
    ]
    last_url = getattr(settings, 'ADDON_URLS_LAST', None)
    if last_url:
        pats.append(
            path('', include(last_url))
        )
    return pats


def i18n_patterns():
    pats = [
        path('', include(url))
        for url in getattr(settings, 'ADDON_URLS_I18N', [])
    ]
    last_url = getattr(settings, 'ADDON_URLS_I18N_LAST', None)
    if last_url:
        pats.append(
            path('', include(last_url))
        )
    return pats

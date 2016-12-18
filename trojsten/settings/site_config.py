# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseSite(object):
    name = None
    short_name = None
    url = None
    autologin = False
    organizers_email = None


class InternalSite(BaseSite):
    has_logo = False
    is_login_provider = False
    folder = 'trojsten'
    theme_color = '#5f7de4'
    autologin = True
    facebook_page = 'https://www.facebook.com/Trojsten'
    googleplus_page = 'http://trojsten.sk'


class KSPSite(InternalSite):
    name = 'Korešpondenčný seminár z programovania'
    short_name = 'KSP'
    url = 'http://ksp.sk'
    organizers_email = 'ksp-info@ksp.sk'
    has_logo = True
    folder = 'ksp'
    facebook_page = 'https://www.facebook.com/KSPsk'
    googleplus_page = 'http://www.ksp.sk'
    theme_color = '#818f3d'


class PraskSite(KSPSite):
    name = 'Prask'
    short_name = 'Prask'
    url = 'http://prask.ksp.sk'
    has_logo = True
    folder = 'prask'
    facebook_page = 'https://www.facebook.com/prask.ksp'
    googleplus_page = 'https://prask.ksp.sk'


class FKSSite(InternalSite):
    name = 'Fyzikálny korešpondenčný seminár'
    short_name = 'FKS'
    url = 'http://fks.sk'
    organizers_email = 'otazky@fks.sk'
    has_logo = True
    folder = 'fks'
    facebook_page = 'http://fks.sk'
    googleplus_page = 'http://fks.sk'
    theme_color = '#e39f3c'


class UFOSite(FKSSite):
    name = 'Korešpondenčný seminár UFO'
    short_name = 'UFO'
    url = 'http://ufo.fks.sk'
    has_logo = True
    folder = 'ufo'
    facebook_page = 'http://ufo.fks.sk'
    googleplus_page = 'http://ufo.fks.sk'


class FXSite(FKSSite):
    name = 'Korešpondenčný seminár FX'
    short_name = 'FX'
    url = 'http://fx.fks.sk'
    has_logo = True
    folder = 'fx'
    facebook_page = 'http://fx.fks.sk'
    googleplus_page = 'http://fx.fks.sk'


class KMSSite(BaseSite):
    name = 'Korešpondenčný matematický seminár'
    short_name = 'KMS'
    url = 'http://kms.sk'
    folder = 'kms'
    facebook_page = 'https://www.facebook.com/pages/KMS/144730632208936'
    googleplus_page = 'http://kms.sk'
    theme_color = '#8c3be3'


class TrojstenSite(BaseSite):
    name = 'Trojsten'
    short_name = 'Trojsten'
    url = 'http://trojsten.sk'
    folder = 'trojsten'
    facebook_page = 'https://www.facebook.com/Trojsten'
    googleplus_page = 'http://trojsten.sk'
    theme_color = '#5f7de4'


class LoginSite(InternalSite):
    name = 'Trojsten Login'
    short_name = 'Login'
    url = 'http://login.trojsten.sk'
    is_login_provider = True


class WikiSite(InternalSite):
    name = 'Trojstenová Wikipédia'
    short_name = 'Wiki'
    url = 'http://wiki.trojsten.sk'
    folder = 'wiki'


class IKSSite(BaseSite):
    name = 'Korešpondenčný seminár iKS'
    short_name = 'iKS'
    url = 'http://iksko.org'


SITES = {
    1: KSPSite(),
    2: PraskSite(),
    3: FKSSite(),
    4: KMSSite(),
    5: TrojstenSite(),
    6: WikiSite(),
    7: UFOSite(),
    8: FXSite(),
    9: IKSSite(),
    10: LoginSite(),
}

# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def login_root_view(request):
    # @TODO: vymyslieť čo tu bude
    return render(request, 'trojsten/login/base.html')

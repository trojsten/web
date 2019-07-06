from django.conf.urls import url

from .views import solved

urlpatterns = [
    url(r"^1/nasiel_si_velmi_kratky_cyklus/", solved, {"level": 1}),
    url(r"^2/int_ti_obcas_pretecie/", solved, {"level": 2}),
    url(r"^3/da_sa_to_aj_bruteforcit/", solved, {"level": 3}),
    url(r"^4/moznosti_na_seedy_neni_az_tak_vela/", solved, {"level": 4}),
]

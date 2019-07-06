from django.conf.urls import url

from .views import solved

urlpatterns = [
    url(r"^1/uplne_najtajnejsi_link_ktory_nikdy_nijaky_fiskus_neuhadne/", solved, {"level": 1}),
    url(r"^2/heslo_je_afmnskm/", solved, {"level": 2}),
    url(r"^3/je_naozaj_tazke_vymysliet_kreativny_tazko_hadatelny_link/", solved, {"level": 3}),
    url(r"^4/poculi_ste_o_spravnom_konovi_baterie_zosivajucom/", solved, {"level": 4}),
    url(r"^5/dufam_ze_ste_tuto_podulohu_vyriesili_poctivo/", solved, {"level": 5}),
    url(r"^6/tam_kde_nic_nie_je_sa_ani_nic_nemoze_stratit/", solved, {"level": 6}),
]

import collections

LIST_LEVEL_PWD = "03f47b6adf93a3"

Level = collections.namedtuple("Level", ["url", "source_fname", "hint"])

LEVELS = [
    Level("letsplay", "mouse.html", "Myši majú dobrý čuch."),
    Level("kungfu", "popup.html", "Čo ak by tam nebol ten otravný popup?"),
    Level("domadobre", "request.html", "GET parameter"),
    Level("pokuta", "buttons.html", "Skús zistiť, ktoré tlačidlo je užitočné."),
    Level("gulas", "stlpce.html", "Je to postava z animáku :)"),
    Level("olaf", "heslo.html", "Nebolo už niekde meno a heslo?"),
    Level("legruyere", "images.html", "V rohoch sa skrývajú kusy známeho kódovania."),
    Level(
        "chickpea",
        "list.html",
        "Parametrami v URL môžeš získať viac riadkov. Jeden z nich má v sebe heslo.",
    ),
    Level(LIST_LEVEL_PWD, "subor.html", "Nahrávka je nejaká divná, žeby otočená?"),
    Level("stracciatella", "finish.html", "Hmm, žiadny hint tu nie je, vyhral/a si :P"),
]

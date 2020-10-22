class Level:
    def __init__(self, url, source_fname, hint):
        self.url = url
        self.source_fname = source_fname
        self.hint = hint


LEVELS = [
    Level("letsplay", "pexeso.html", "Je to skoro ako pexeso."),
    Level("level2", "urlchange.html", "Pozri sa na URL aktuálnej stránky :)"),
    Level("level3", "insource.html", "Ak heslo nevidno na stránke, mohlo sa zašiť niekam do kódu."),
    Level("malina", "morse.html", "Jeden pes je dlhý, druhý zase guľatý. Nie sú to Morseho psy?"),
    Level(
        "woof",
        "button.html",
        (
            "Prefix ukazoval, že cez Developer Tools (F12) môžeme meniť stránku. Skús tak spraviť "
            "tlačidlo stlačitelné. Anglicky slovo 'disabled' znamená 'zakázaný' :P"
        ),
    ),
    Level(
        "slamastika",
        "validator.html",
        "Čo to po tebe len ten validátor chce? Nie je niekde kód, podľa ktorého validuje?",
    ),
    Level(
        "m3dv3d",
        "cookie.html",
        'Na obrázku je sušienka, anglicky "cookie". Tie tuším Prefix spomínal vo videu :P',
    ),
    Level(
        "hihihihi",
        "input.html",
        (
            "Ale veď naraz môžem objednať iba 10 rezňov! Hmm, nedá sa tento limit zväčšiť "
            "kdesi v kóde?"
        ),
    ),
    Level("abrakadabra", "abeceda.html", "Koľko písmen má ABECEDA?"),
    Level("7", "finish.html", "Hmm, žiadny hint tu nie je, vyhral/a si :P"),
]

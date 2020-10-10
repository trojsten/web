class Level:
    def __init__(self, url, source_fname, hint):
        self.url = url
        self.source_fname = source_fname
        self.hint = hint
        
LEVELS = [
    Level("letsplay", "pexeso.html", "Hint k levelu 1."),
    Level("level2", "urlchange.html", "Hint k levelu 2."),
    Level("level3", "insource.html", "Hint k levelu 3."),
    Level("malina", "morse.html", "Hint k levelu č."),
    Level("morseout", "button.html", "Hint k levelu č."),
    Level("slamastika", "validator.html", "Hint k levelu č."),
    Level("b19bk", "cookie.html", "Hint k levelu č."),
    Level("hihihihi", "input.html", "Hint k levelu č."),
    Level("abrakadabra", "abeceda.html", "Hint k levelu č."),
    Level("7", "finish.html", "Hmm, žiadny hint tu nie je, vyhral/a si :P")
]
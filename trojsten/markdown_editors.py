from wiki.editors.markitup import MarkItUp


class TrojstenMarkItUp(MarkItUp):
    class AdminMedia:
        css = {
            "all": ("wiki/markitup/skins/simple/style.css", "wiki/markitup/sets/admin/style.css")
        }
        js = (
            "wiki/markitup/admin.init.js",
            "wiki/markitup/jquery.markitup.js",
            "wiki/markitup/sets/admin/set.js",
        )

    class Media:
        css = {"all": ("css/markitup-dark.css",)}
        js = (
            "wiki/markitup/frontend.init.js",
            "wiki/markitup/jquery.markitup.js",
            "wiki/markitup/sets/frontend/set.js",
        )

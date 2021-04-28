def _import_modules():
    import os

    global __all__
    __all__ = []

    _globals, _locals = globals(), locals()
    for f in os.listdir(__name__):
        if f[0] != "_" and f.endswith("py"):
            file_name = f.split(".")[0]
            module = ".".join([__name__, file_name])
            try:
                imported = __import__(module, _globals, _locals, [file_name])
                for name in imported.__dict__:
                    if not name.startswith("_"):
                        _globals[name] = imported.__dict__[name]
                        __all__.append(name)
            except:
                print("Error!")
            

    # print(__all__)


_import_modules()
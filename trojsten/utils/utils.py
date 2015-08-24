def is_true(value):
    '''Converts GET parameter value to bool
    '''
    return bool(value) and value.lower() not in ('false', '0')

try:
    from django.utils.module_loading import import_string
except ImportError:
    from importlib import import_module

    from django.utils import six

    def import_string(dotted_path):
        """
        Import a dotted module path and return the attribute/class designated by the
        last name in the path. Raise ImportError if the import failed.
        Borrowed from Django 1.7.
        """
        try:
            module_path, class_name = dotted_path.rsplit('.', 1)
        except ValueError:
            msg = "%s doesn't look like a module path" % dotted_path
            six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

        module = import_module(module_path)

        try:
            return getattr(module, class_name)
        except AttributeError:
            msg = 'Module "%s" does not define a "%s" attribute/class' % (
                dotted_path, class_name)
            six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

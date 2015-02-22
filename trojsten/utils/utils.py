def is_true(value):
    '''Converts GET parameter value to bool
    '''
    return bool(value) and value.lower() not in ('false', '0')

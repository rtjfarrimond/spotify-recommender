def escape_forwardslash(string):
    ''' Replaces forward slash with colon.

    File basename cannot contain forwardslashes (/).
    On Unix-like systems. Using a colon (:) in the basename will
    convert to a forwardslash when viewed.
    '''
    return string.replace('/', ':')

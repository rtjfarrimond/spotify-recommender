def escape_forwardslash_in_basename(string):
    ''' Replaces forward slash with colon.

    File basename cannot contain forwardslashes (/).
    On Unix-like systems, using a colon (:) in the basename will
    convert to a forwardslash when viewed.
    '''
    return string.replace('/', ':')

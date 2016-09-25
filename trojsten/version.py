import os


def get_version_string():
    version_file = os.path.join(os.path.dirname(__file__), '..', 'version.txt')
    version_string = ''
    if os.path.isfile(version_file):
        with open(version_file) as f:
            version_string = f.readline().strip()
    return version_string

version_string = get_version_string()

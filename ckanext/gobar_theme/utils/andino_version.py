import codecs
import os


def get_portal_andino_version():
    os.chdir('/')
    portal_dir = os.path.abspath(os.path.join(os.getcwd(), 'portal/'))
    try:
        with codecs.open(os.path.join(portal_dir, 'version')) as f:
            version = f.read().strip()
    except IOError:
        version = None
    return version

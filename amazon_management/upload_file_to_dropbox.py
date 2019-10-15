"""Upload the contents of your Downloads folder to Dropbox.
This is an example app for API v2.
"""

from __future__ import print_function

import argparse
import contextlib
import datetime
import os
import six
import sys
import time
import unicodedata
import re
if sys.version.startswith('2'):
    input = raw_input  # noqa: E501,F821; pylint: disable=redefined-builtin,undefined-variable,useless-suppression

import dropbox
from amazon_management import logger
from amazon_management.utils import YamlConfigLoader
# OAuth2 access token.  TODO: login etc.
TOKEN = 'TKhVU89diDAAAAAAAAAADZTm3OA4PWgv9sAM9wBKyUBeVEljlsgbJdAmUxq52XkI'


parser = argparse.ArgumentParser(description='Sync ~/Downloads to Dropbox')
parser.add_argument('folder', nargs='?', default='Downloads',
                    help='Folder name in your Dropbox')
parser.add_argument('rootdir', nargs='?', default='~/Downloads',
                    help='Local directory to upload')
parser.add_argument('--token', default=TOKEN,
                    help='Access token '
                    '(see https://www.dropbox.com/developers/apps)')
parser.add_argument('--yes', '-y', action='store_true',
                    help='Answer yes to all questions')
parser.add_argument('--no', '-n', action='store_true',
                    help='Answer no to all questions')
parser.add_argument('--default', '-d', action='store_true',
                    help='Take default answer on all questions')

def main():
    """Main program.
    Parse command line, then iterate over files and directories under
    rootdir and upload all files.  Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """

    config_path = './inventory_download.yml'
    config_path = os.path.abspath(os.path.expanduser(config_path))
    if not os.path.isfile(config_path):
        logger.error('Could not find configuration file - %s', config_path)
        sys.exit(0)

    cl = YamlConfigLoader(config_path)
    config = cl.load()

    folder = config['account']['acc']
    print("folder", folder)

    args = parser.parse_args()

    if not args.token:
        print('--token is mandatory')
        sys.exit(2)

    rootdir = os.path.expanduser(args.rootdir)
    print('Dropbox folder name:', folder)
    print('Local directory:', rootdir)
    if not os.path.exists(rootdir):
        print(rootdir, 'does not exist on your filesystem')
        sys.exit(1)
    elif not os.path.isdir(rootdir):
        print(rootdir, 'is not a folder on your filesystem')
        sys.exit(1)

    dbx = dropbox.Dropbox(args.token)

    for dn, dirs, files in os.walk(rootdir):
        subfolder = dn[len(rootdir):].strip(os.path.sep)
        listing = list_folder(dbx, folder, subfolder)
        print('Descending into', subfolder, '...')
        # First do all the files.
        today = time.strftime("%m-%y-%d", time.localtime())
        name = ''
        for file in files:
            if re.match(r'All\+Listings\+Report\+[0-9]{2}-[0-9]{2}-[0-9]{4}(.*)\.txt', file):
                if name == '':
                    name = file
                else:
                    full_path = os.path.join(dn, file)
                    fullname = os.path.join(dn, name)
                    if os.path.getmtime(fullname) < os.path.getmtime(full_path):
                        name = file
                        print("name", name)

        if not isinstance(name, six.text_type):
            name = name.decode('utf-8')
        nname = unicodedata.normalize('NFC', name)

        if nname in listing:
            md = listing[nname]
            mtime = os.path.getmtime(fullname)
            print("mtime", mtime)
            mtime_dt = datetime.datetime(*time.gmtime(mtime)[:6])
            print("mtime_dt", mtime_dt)
            size = os.path.getsize(fullname)
            if (isinstance(md, dropbox.files.FileMetadata) and
                    mtime_dt == md.client_modified and size == md.size):
                print(name, 'is already synced [stats match]')

        else:
            upload(dbx, fullname, folder, subfolder, name)


def list_folder(dbx, folder, subfolder):
    """List a folder.
    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
    print("path", path)
    print("dbx", dbx)
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        with stopwatch('list_folder'):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumed empty:', err)
        return {}
    else:
        rv = {}
        for entry in res.entries:
            rv[entry.name] = entry
        return rv


def upload(dbx, fullname, folder, subfolder, name, overwrite=False):
    """Upload a file.
    Return the request response, or None in case of error.
    """


    path = '/%s/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'), name)
    while '//' in path:
        path = path.replace('//', '/')
    mode = (dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add)
    mtime = os.path.getmtime(fullname)
    with open(fullname, 'rb') as f:
        data = f.read()
    with stopwatch('upload %d bytes' % len(data)):
        try:
            res = dbx.files_upload(
                data, path, mode,
                client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
    print('uploaded as', res.name.encode('utf8'))
    return res


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))


if __name__ == '__main__':
    main()
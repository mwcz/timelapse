#!/usr/bin/env python

import locale
import os
import pprint
import shlex
import sys
import argparse

from dropbox import client, rest

# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
APP_KEY = open('app_key').readline()
APP_SECRET = open('app_secret').readline()

def command(login_required=True):
    """a decorator for handling authentication and exceptions"""
    def decorate(f):
        def wrapper(self, args):
            if login_required and self.api_client is None:
                print("Please 'login' to execute this command\n")
                return

            try:
                return f(self, *args)
            except TypeError, e:
                print(str(e) + '\n')
            except rest.ErrorResponse, e:
                msg = e.user_error_msg or str(e)
                print('Error: %s\n' % msg)

        wrapper.__doc__ = f.__doc__
        return wrapper
    return decorate

class DropboxTerm():
    TOKEN_FILE = "token_store.txt"

    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.current_path = ''

        self.parser = argparse.ArgumentParser()
        # create argparse entry for each command
        all_names = dir(self)
        cmd_names = []
        for name in all_names:
            if name[:3] == 'do_':
                cmd_names.append(name[3:])
        cmd_names.sort()
        self.parser.add_argument('command', action='store', choices=cmd_names)
        self.parser.add_argument('args', action='store', nargs='*')
        cmd_args = self.parser.parse_args()

        self.api_client = None
        try:
            token = open(self.TOKEN_FILE).read()
            self.api_client = client.DropboxClient(token)

            # find and execute the desired command
            getattr(self, 'do_' + cmd_args.command)(cmd_args.args)
        except IOError:
            pass # don't worry if it's not there

    @command()
    def do_ls(self):
        """list files in current remote directory"""
        resp = self.api_client.metadata(self.current_path)

        if 'contents' in resp:
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                encoding = locale.getdefaultlocale()[1]
                print(('%s\n' % name).encode(encoding))

    @command()
    def do_cd(self, path):
        """change current working directory"""
        if path == "..":
            self.current_path = "/".join(self.current_path.split("/")[0:-1])
        else:
            self.current_path += "/" + path

    @command(login_required=False)
    def do_login(self):
        """log in to a Dropbox account"""
        flow = client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        authorize_url = flow.start()
        print("1. Go to: " + authorize_url + "\n")
        print("2. Click \"Allow\" (you might have to log in first).\n")
        print("3. Copy the authorization code.\n")
        code = raw_input("Enter the authorization code here: ").strip()

        try:
            access_token, user_id = flow.finish(code)
        except rest.ErrorResponse, e:
            print('Error: %s\n' % str(e))
            return

        with open(self.TOKEN_FILE, 'w') as f:
            f.write(access_token)
        self.api_client = client.DropboxClient(access_token)

    @command()
    def do_logout(self):
        """log out of the current Dropbox account"""
        self.api_client = None
        os.unlink(self.TOKEN_FILE)
        self.current_path = ''

    @command()
    def do_cat(self, path):
        """display the contents of a file"""
        f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + path)
        print(f.read())
        print("\n")

    @command()
    def do_mkdir(self, path):
        """create a new directory"""
        self.api_client.file_create_folder(self.current_path + "/" + path)

    @command()
    def do_rm(self, path):
        """delete a file or directory"""
        self.api_client.file_delete(self.current_path + "/" + path)

    @command()
    def do_mv(self, from_path, to_path):
        """move/rename a file or directory"""
        self.api_client.file_move(self.current_path + "/" + from_path,
                                  self.current_path + "/" + to_path)

    @command()
    def do_share(self, path):
        print self.api_client.share(path)['url']

    @command()
    def do_account_info(self):
        """display account information"""
        f = self.api_client.account_info()
        pprint.PrettyPrinter(indent=2).pprint(f)

    @command(login_required=False)
    def do_exit(self):
        """exit"""
        return True

    @command()
    def do_get(self, from_path, to_path):
        """
        Copy file from Dropbox to local file and print out the metadata.

        Examples:
        get file.txt ~/dropbox-file.txt
        """
        to_file = open(os.path.expanduser(to_path), "wb")

        f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + from_path)
        print 'Metadata:', metadata
        to_file.write(f.read())

    @command()
    def do_thumbnail(self, from_path, to_path, size='large', format='JPEG'):
        """
        Copy an image file's thumbnail to a local file and print out the
        file's metadata.

        Examples:
        thumbnail file.txt ~/dropbox-file.txt medium PNG
        """
        to_file = open(os.path.expanduser(to_path), "wb")

        f, metadata = self.api_client.thumbnail_and_metadata(
                self.current_path + "/" + from_path, size, format)
        print 'Metadata:', metadata
        to_file.write(f.read())

    @command()
    def do_put(self, from_path, to_path):
        """
        Copy local file to Dropbox

        Examples:
        put ~/test.txt dropbox-copy-test.txt
        """
        from_file = open(os.path.expanduser(from_path), "rb")

        self.api_client.put_file(self.current_path + "/" + to_path, from_file)

    @command()
    def do_search(self, string):
        """Search Dropbox for filenames containing the given string."""
        results = self.api_client.search(self.current_path, string)
        for r in results:
            print("%s\n" % r['path'])

    # the following are for command line magic and aren't Dropbox-related
    def emptyline(self):
        pass

    def do_EOF(self, line):
        print('\n')
        return True

    def parseline(self, line):
        parts = shlex.split(line)
        if len(parts) == 0:
            return None, None, line
        else:
            return parts[0], parts[1:], line


def main():
    if APP_KEY == '' or APP_SECRET == '':
        exit("You need to set your APP_KEY and APP_SECRET!")
    term = DropboxTerm(APP_KEY, APP_SECRET)

if __name__ == '__main__':
    main()

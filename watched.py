#!/usr/bin/python

from deluge.ui.client import client
# Import the reactor module from Twisted - this is for our mainloop
from twisted.internet import reactor
# Set up the logger to print out errors
from deluge.log import setupLogger

import optparse
import os.path
import re
import shutil
import time

class Deluge:
    def __init__(self, options, fnames):
        setupLogger()
        self._deluge = client.connect()
        self._deluge.addCallback(self.on_connect_success)
        self._deluge.addErrback(self.on_error)
        self.watched_path = self.ensure_exists(options['watched-local'])
        self.towatch_remote_path = self.ensure_exists(options['towatch-remote'])
        self.fnames = fnames
        self.re_fnames = []
        for fname in fnames:
            self.re_fnames.append(re.compile(fname, re.IGNORECASE))
        self.to_move_storage = []  # keep torrent, move data
        self.to_move_backup = []  # remove torrent, move data to backup
        self.to_remove = []  # remove torrent and data
        self.options = options
        self.finish_location = None

    def on_get_config_value(self, value, key):
        if key == 'move_completed_path':
            self.finish_location = value
        #print "%s: %s" % (key, value)

    def ensure_exists(self, directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)
        return directory

    def done(self):
        # Disconnect from the daemon once we've got what we needed
        client.disconnect()
        # Stop the twisted main loop and exit
        reactor.stop()

    def on_move_storage(self, unused_info):
        if self.to_move_storage:
            self.move_storage()
        else:
            time.sleep(1)
            self.done()

    def move_storage(self):
        hash_val, fname = self.to_move_storage.pop()
        print 'Moving %s to %s' % (fname, self.watched_path)
        client.core.move_storage([hash_val], self.watched_path).addCallback(self.on_move_storage)

    def on_get_torrents_move_storage(self, torrents):
        found = []
        found_one = False
        for hashval, torrent_info in torrents.iteritems():
            if torrent_info['progress'] == 100.0:
                save_path = torrent_info['save_path']
                for file_info in torrent_info['files']:
                    fname = file_info['path']
                    for re_fname in self.re_fnames:
                        if re_fname.search(fname):
                            found_one = True
                            if self.watched_path in save_path:
                                print '%s already in watched path' % fname
                            else:
                                found.append((hashval, torrent_info['files']))
        if len(found) == len(self.fnames):
            self.to_move_storage = found[:]
            self.move_storage()
        elif not found:
            if not found_one:
                print '%s not found' % ', '.join(self.fnames)
            self.done()
        else:
            print 'Found %d matches for %s' % (len(found), ', '.join(self.fnames))
            self.done()

    def on_get_torrents_list(self, torrents):
        files = []
        for hashval, torrent_info in torrents.iteritems():
            if torrent_info['progress'] == 100.0:
                save_path = torrent_info['save_path']
                if self.watched_path in save_path:
                    continue
                for file_info in torrent_info['files']:
                    fname = file_info['path']
                    files.append(fname)
        if files:
            print 'List of finished torrent files:'
            for fname in files:
                print fname
        else:
            print 'No files 100% done that\'s not watched'
        self.done()

    def on_get_torrents_orphans(self, torrents):
        print 'Orphan files'
        fnames = set()
        for hashval, torrent_info in torrents.iteritems():
            save_path = torrent_info['save_path']
            for file_info in torrent_info['files']:
                fnames.add(file_info['path'])

        for fname in os.listdir(self.finish_location):
            fullname = os.path.join(self.finish_location, fname)
            if os.path.isdir(fullname):
                continue
            if fname not in fnames:
                print fname

        self.done()

    # Remove torrent
    def on_remove_torrent(self, unused_info):
        if self.to_remove:
            self.remove_torrent()
        else:
            time.sleep(1)
            self.done()

    def remove_torrent(self):
        hash_val, fname = self.to_remove.pop()
        print 'Removing torrent and data %s' % (fname)
        client.core.remove_torrent(hash_val, remove_data=True).addCallback(self.on_remove_torrent)

    def on_get_torrents_remove_torrent(self, torrents):
        found = []
        found_one = False
        for hashval, torrent_info in torrents.iteritems():
            if torrent_info['progress'] == 100.0:
                for file_info in torrent_info['files']:
                    fname = file_info['path']
                    for re_fname in self.re_fnames:
                        if re_fname.search(fname):
                            found.append((hashval, fname))
        if len(found) == len(self.fnames):
            self.to_remove = found[:]
            self.remove_torrent()
        elif not found:
            print '%s not found' % ', '.join(self.fnames)
            self.done()
        else:
            print 'Found %d matches for %s' % (len(found), ', '.join(self.fnames))
            self.done()

    # Move torrent data to backup
    def on_move_torrent_data(self, unused, torrent_info):
        save_path = torrent_info['save_path']
        for file_info in torrent_info['files']:
            fname = file_info['path']
            from_fname = os.path.join(save_path, fname)
            to_fname = os.path.join(self.towatch_remote_path, fname)
            print 'Moving %s to %s' % (fname, self.towatch_remote_path)
            shutil.move(from_fname, to_fname)

        if self.to_move_backup:
            self.move_torrent_data()
        else:
            time.sleep(1)
            self.done()

    def move_torrent_data(self):
        hash_val, torrent_info = self.to_move_backup.pop()
        print ('Removing torrent %s' % torrent_info['files'][0]['path'])
        client.core.remove_torrent(hash_val, remove_data=False).addCallback(
                self.on_move_torrent_data, torrent_info)

    def on_get_torrents_make_space(self, torrents):
        found = []
        found_one = False
        for hashval, torrent_info in torrents.iteritems():
            if torrent_info['progress'] == 100.0:
                for file_info in torrent_info['files']:
                    fname = file_info['path']
                    for re_fname in self.re_fnames:
                        if re_fname.search(fname):
                            found.append((hashval, torrent_info))
        if found and len(found) == len(self.fnames):
            self.to_move_backup = found[:]
            self.move_torrent_data()
        elif not found:
            print '%s not found' % ', '.join(self.fnames)
            self.done()
        else:
            print 'Found %d matches for %s' % (len(found), ', '.join(self.fnames))
            self.done()

    # We create a callback function to be called upon a successful connection
    def on_connect_success(self, result):
        # Request the config value for the key 'finish_location'
        client.core.get_config_value("move_completed_path").addCallback(self.on_get_config_value, "move_completed_path")
        filters = {}
        cols = ['files', 'progress', 'save_path']
        callback = None
        if self.options['orphans']:
            callback = self.on_get_torrents_orphans
        elif self.fnames and self.options['remove']:
            callback = self.on_get_torrents_remove_torrent
        elif self.fnames and self.options['make-space']:
            callback = self.on_get_torrents_make_space
        elif self.fnames:
            callback = self.on_get_torrents_move_storage
        else:
            callback = self.on_get_torrents_list
        client.core.get_torrents_status(filters, cols).addCallback(callback)

    def on_error(self, result):
        print 'Error occurred'
        print "result:", result

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option(
        '-o', '--orphans', dest='orphans', action='store_true',
        help='Files that don\'t belong')
    parser.add_option(
        '-r', '--rm', dest='remove', action='store_true',
        help='Remove the torrent and data')
    parser.add_option(
        '-m', '--move', dest='make_space', action='store_true',
        help='Make space, move to hard disk, remove .torrent')
    options, args = parser.parse_args()
    options = {
            'watched-local': os.path.expanduser('~/finished/watched'),
            'towatch-remote': os.path.expanduser('/media/backup/videos/towatch'),
            'orphans': options.orphans,
            'remove': options.remove,
            'make-space': options.make_space,
    }
    d = Deluge(
            options,
            args)
    # Run the twisted main loop to make everything go
    reactor.run()

#!/usr/bin/python
"""
Import photographs from SD media when mounted.
Opens up a dialog with PyGTK to show you where it's
going to put the images, ordered by date.

Some Features:
- Checks for .cr2 and identical .jpg files and copies only the .cr2 version and
  removes the (duplicate) .jpg version.
- Unmounts the drive after copying so you can just remove the media without
  hunting for the unmount drive menu entry.
- Copies also any other media found (like videos).
- Moves files one at a time, deletes source only after copied successfully.


TODO:
- Would be nice to make sense of parties that go over midnight, and keep on one
  date only.
"""

import pygtk
pygtk.require('2.0')
import gobject
import gtk
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import time

LOGFILE = '%s/import-photos.log' % (os.path.dirname(__file__))
TODIR = '~/Pictures'
MEDIA = '/media'
DIR_FORMAT = '%Y/%m/%d'  # ex. 2011/12/01

class FileInfo:
    """Information about a file or two."""
    def __init__(self, from_dir, from_name):
        self.from_dir = from_dir
        self.original_name = from_name
        self.dupe = None

    def ComparableName(self):
        return os.path.splitext(self.original_name.lower())[0]

    def SetDupe(self, dupe_name):
        """We want .cr2 instead of .jpg.
        Return:
            True if it's dupe, False otherwise.
        """
        new_root, new_ext = os.path.splitext(dupe_name.lower())
        old_root, old_ext = os.path.splitext(self.original_name.lower())
        if new_ext == '.jpg':
            self.dupe = dupe_name
            return True
        elif old_ext == '.jpg':
            self.dupe = self.original_name
            self.original_name = dupe_name
            return True
        return False


    def MoveFile(self, dest_dir, log):
        from_file = os.path.join(self.from_dir, self.original_name)
        mtime = os.stat(from_file).st_mtime
        folder = os.path.join(dest_dir, time.strftime(DIR_FORMAT,
            (time.localtime(mtime))))
        if not os.path.isdir(folder):
            os.makedirs(folder)
        dest_file = os.path.join(folder, self.original_name.lower())
        log('%s\n' % dest_file)
        shutil.move(from_file, dest_file)
        if self.dupe:
            dupe_name = os.path.join(self.from_dir, self.dupe)
            log('Deleting %s\n' % dupe_name)
            os.unlink(dupe_name)


class OutputWindow:
    def delete_event(self, widget, event, data=None):
        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self, fromdir, todir):
        self.fromdir = fromdir
        self.todir = todir

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)

        # Sets the border width of the window.
        self.window.set_border_width(10)
        self.window.resize(500, 700)

        self.button = gtk.Button('Move Files')

        # When the button receives the 'clicked' signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.close_button_handler_id = self.button.connect('clicked', self.OnButton)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        sw.add(self.textview)

        vbox = gtk.VBox()
        vbox.pack_start(sw)
        vbox.pack_start(self.button, False)

        self.window.add(vbox)
        self.window.show_all()
        self.window.set_default(self.button)
        self.window.set_focus(self.button)
        self.ShowIntro()

    def OnButton(self, widget, data=None):
        self.button.set_sensitive(False)
        thr = threading.Thread(target=self.MoveFiles)
        thr.start()

    def OnClose(self, widget, data=None):
        self.destroy(widget)

    def SetCloseButton(self):
        self.button.set_label('Close')
        self.button.disconnect(self.close_button_handler_id)
        self.button.connect('clicked', self.OnClose)
        self.button.set_sensitive(True)
        self.window.set_focus(self.button)

    def MoveFiles(self):
        if not self.fromdir:
            self.LogLine('No folder to copy from')
            self.SetCloseButton()
            return
        files = []
        fmap = {}
        for fname in os.listdir(self.fromdir):
            fi = FileInfo(self.fromdir, fname)
            cname = fi.ComparableName()
            if cname in fmap:
                if not fmap[cname].SetDupe(fname):
                    fmap[cname] = fi
                    files.append(fi)
            else:
                fmap[cname] = fi
                files.append(fi)
        self.LogLine('Starting...\n')
        for fi in files:
            fi.MoveFile(self.todir, self.LogLine)

        self.LogLine('Eject media.\n')
        UnmountMedia(self.fromdir)
        self._LogLine('%d files copied to %r\n' % (len(files), self.todir))
        self.SetCloseButton()

    def ShowIntro(self):
        self._LogLine('Scott\'s Image Copying Program\n\n')
        self._LogLine('From %r\n' % self.fromdir)
        self._LogLine('To %r\n' % self.todir)
        self._LogLine('Press button to start\n')

    def LogLine(self, line):
        gtk.gdk.threads_enter()
        self._LogLine(line)
        gtk.gdk.threads_leave()

    def _LogLine(self, line):
        enditer = self.textbuffer.get_end_iter()
        self.textbuffer.place_cursor(enditer)
        self.textbuffer.insert(enditer, line)
        self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0.1)

    def main(self):
        gtk.main()


def GuessDir(dirname):
    if len(sys.argv) > 1 and sys.argv[1].startswith('/media/'):
        logging.info('Using passed argv[1] %r' % sys.argv[1])
        dirname = sys.argv[1]
        return _DcimSubdir(dirname)

    for dname in os.listdir(dirname):
        subdir = _DcimSubdir(os.path.join(dirname, dname))
        if subdir:
            return subdir
    logging.error('Unable to find an appropriate media directory')
    return None

def _DcimSubdir(dirname):
    fullpath = os.path.join(dirname, 'DCIM')
    if os.path.exists(fullpath):
        dirs = os.listdir(fullpath)
        return os.path.join(fullpath, dirs[-1])
    return None

def UnmountMedia(media):
    re_toptwo = re.compile(r'(/[^/]+/[^/]+)')
    grps = re_toptwo.search(media)
    if not grps:
        logging.error('Unable to find media directory from %r' % media)
        exit(-1)
    top_two = grps.group(1)
    logging.info('Unmounting media %r' % top_two)
    # sudo apt-get install pmount
    subprocess.call(['pumount', top_two])

def Main():
    gobject.threads_init()
    gtk.gdk.threads_init()
    logging.basicConfig(filename=LOGFILE, level=logging.INFO)
    todir = os.path.expanduser(TODIR)
    fromdir = GuessDir(MEDIA)
    output = OutputWindow(fromdir, todir)
    output.main()


if __name__ == '__main__':
    Main()

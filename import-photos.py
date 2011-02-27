#!/usr/bin/python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import logging
import os
import re
import subprocess
import sys
import stat
import threading
import time

LOGFILE = '%s/import-photos.log' % (os.path.dirname(__file__))
TODIR = '~/Pictures'
MEDIA = '/media'

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
        self.button.connect('clicked', self.OnButton)

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

    def MoveFile(self, fname):
        mtime = os.stat(os.path.join(self.fromdir, fname)).st_mtime
        folder = os.path.join(self.todir, time.strftime("%Y/%m/%d",
            (time.localtime(mtime))))
        self.LogLine('%s - %s\n' % (fname, folder))
        destfile = os.path.join(folder, fname)

    def MoveFiles(self):
        self.LogLine('Starting...\n')
        count = 0
        for fname in os.listdir(self.fromdir):
            self.MoveFile(fname)
            count += 1
        self.LogLine('Eject media.\n')
        UnmountMedia(self.fromdir)
        self._LogLine('%d files copied to %r\n' % (count, self.todir))

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

#!/usr/bin/python
"""Fix the photos with the wrong date.
I put the date on the camera 8 months off.
This uses the pyexiv2 library to fix the date-time tags.
It also moves the file to the correct folder.
"""

import datetime
import glob
import os
import pyexiv2


def read_meta(fname):
  metadata = pyexiv2.ImageMetadata(fname)
  metadata.read()
  model = metadata['Exif.Image.Model']
  if 'T2i' not in model.value:
    return
  orig_tag = metadata['Exif.Photo.DateTimeOriginal']
  orig_tag.value = orig_tag.value.replace(month=orig_tag.value.month + 8)
  digit_tag = metadata['Exif.Photo.DateTimeDigitized']
  digit_tag.value = digit_tag.value.replace(month=digit_tag.value.month + 8)
  to_name = '%02d/%s' % (digit_tag.value.month, os.path.basename(fname))
  print 'Write %s' % fname
  metadata.write()

def move_to_correct_folder(fname):
  metadata = pyexiv2.ImageMetadata(fname)
  metadata.read()
  model = metadata['Exif.Image.Model']
  if 'T2i' not in model.value:
    return
  orig_tag = metadata['Exif.Photo.DateTimeOriginal']
  to_name = '%02d/%02d/%s' % (orig_tag.value.month, orig_tag.value.day, os.path.basename(fname))
  to_name = fname[0:-len(to_name)] + to_name
  if to_name != fname:
    pathname = os.path.dirname(to_name)
    if not os.path.exists(pathname):
      os.makedirs(pathname)
    print 'mv %s %s' % (fname, to_name)
    os.rename(fname, to_name)

def iter_files():
  for fname in glob.glob('/home/scott/Photos/2010/01/09/*.jpg'):
    move_to_correct_folder(fname)


if __name__ == '__main__':
  iter_files()

# encoding: utf8
"""Various information about the underlying ImageMagick library and the
features it supports.

Deliberately not named ``features`` to emphasize that everything herein is
highly specific to ImageMagick and completely out of the library's hands.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import namedtuple

from sanpera._api import ffi, lib
from sanpera.exception import magick_try

FEATURES = frozenset(ffi.string(lib.GetMagickFeatures()).decode('ascii').split(' '))
HAS_OPENMP = 'OpenMP' in FEATURES
HAS_OPENCL = 'OpenCL' in FEATURES
HAS_HDRI = 'HDRI' in FEATURES


# Version number is given as hex; version A.B.C is 0xABC
_out = ffi.new("size_t *")
lib.GetMagickVersion(_out)
VERSION = (
    (_out[0] & 0xf00) >> 8,
    (_out[0] & 0x0f0) >> 4,
    (_out[0] & 0x00f) >> 0,
)
del _out


ImageFormat = namedtuple(
    'ImageFormat',
    ['name', 'description', 'can_read', 'can_write', 'supports_frames', 'mime_type'])

def _get_formats():
    formats = dict()
    formats_by_mime = dict()

    num_formats = ffi.new("size_t *")

    # Snag the list of known supported image formats
    with magick_try() as exc:
        magick_infos = ffi.gc(
            lib.GetMagickInfoList(b"*", num_formats, exc.ptr),
            lib.RelinquishMagickMemory)

    for i in range(num_formats[0]):
        imageformat = ImageFormat(
            name=ffi.string(magick_infos[i].name).decode('latin-1'),
            description=ffi.string(magick_infos[i].description).decode('latin-1'),
            can_read=magick_infos[i].decoder != ffi.NULL,
            can_write=magick_infos[i].encoder != ffi.NULL,
            supports_frames=magick_infos[i].adjoin != 0,
            mime_type=ffi.string(magick_infos[i].mime_type).decode('ascii') if magick_infos[i].mime_type else None,
        )
        formats[imageformat.name.lower()] = imageformat
        formats_by_mime[imageformat.mime_type] = imageformat

    return formats, formats_by_mime

IMAGE_FORMATS, IMAGE_FORMATS_BY_MIMETYPE = _get_formats()

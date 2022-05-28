#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2022 Trent Piepho <tpiepho@gmail.com>

# Extract NSS firmware for R7800 firmware update images.
# Does a new safety checks and automatically determines the NSS firmware image.
#
# Also extracts the Atheros Wifi firmware.

import argparse
import sys
import tempfile
import struct
import os
import io
from pathlib import Path
import datetime

IMAGE_HDR_LEN = 0x80 # DNI image header
KERNEL_PARTSIZE = 0x220000 # Size of kernel partition
UIMAGE_HDR_LEN = 0x40 # Size of uboot header
ROOTFS_OFFSET = KERNEL_PARTSIZE + UIMAGE_HDR_LEN # rootfs image follows kernel header + kernel
SQUASHFS_OFFSET = ROOTFS_OFFSET + UIMAGE_HDR_LEN # squashfs follows rootfs header

parser = argparse.ArgumentParser(description="""
Extract QCom NSS firmware files from an R7800 image.
They are placed into a distribution tarball that can be used when building the
firmware.
Put the output file into the dl directory.
""")

parser.add_argument('fwfile', metavar='IMG_FILE', type=argparse.FileType('rb'), nargs=1,
    help="Name of image file to extract NSS FW from")

if len(sys.argv) == 1:
    parser.print_help()
    exit(1)

args = parser.parse_args()
fw = args.fwfile[0]

# Parse the DNI header at the start of the image
header = {}
with io.BytesIO(fw.read(IMAGE_HDR_LEN)) as dni:
    while line := dni.readline():
        fields = line.partition(b':')
        if fields[1] != b':': break
        header[fields[0]] = fields[2].decode().rstrip()

if b'device' not in header or b'version' not in header:
    print("Doesn't look like this has a R7800 FW image header")
    exit(1)

print(f"Image header detected, fw for {header[b'device']} version {header[b'version']}")

fw.seek(ROOTFS_OFFSET, os.SEEK_SET)
header = struct.unpack_from('>4I', fw.read(UIMAGE_HDR_LEN))
if header[0] != 0x27051956:
    print(f"Got 0x{header[0]:x}, excepted 0x27051956")
    print("Image does not look like a R7800 firmware update file")
    exit(1)
fw.seek(0, os.SEEK_END)
if fw.tell() < header[3] + SQUASHFS_OFFSET:
    print(f"Image appears truncated!")
    print(f"Expected 0x{header[3]:x} bytes of rootfs but only 0x{fw.tell()-SQUASHFS_OFFSET:x} remain")
    exit(1)
  
print(f"Firmware file appears ok, root squashfs size is {header[3]} bytes\n")

with tempfile.TemporaryDirectory() as tmpdir:
    ret = os.system(f"unsquashfs -o {SQUASHFS_OFFSET} -dest {tmpdir}/root {fw.name} /lib/firmware/qca-nss?-retail.bin /lib/firmware/QCA9984")
    if os.waitstatus_to_exitcode(ret) != 0:
        print("Error extracting squashfs image\nMaybe you do not have unsquashfs installed?  It's part of squashfs-tools")
        print("Or maybe it's too old to have the '-o' option?  Try version 4.5 or newer.")
        exit(os.waitstatus_to_exitcode(ret))

    tmp = Path(tmpdir)
    libfw = tmp / 'root' / 'lib' / 'firmware'

    with open(libfw / 'qca-nss1-retail.bin', "rb") as fw1:
        fw1.seek(-0x10000, os.SEEK_END)
        data = fw1.read(0x10000)
        veroffset = data.rindex(b'Version: ') + 9
        verend = data.index(b'-', veroffset)
        verend = data.index(b'-', verend + 1)
        version = data[veroffset:verend].decode('ascii')
        print(f"\nDetect NSS FW version is {version}")
           
    src = tmp / version
    os.mkdir(src)
    os.mkdir(src / 'R')
    os.rename(libfw / 'qca-nss0-retail.bin', src / 'R' / 'retail_router0.bin')
    os.rename(libfw / 'qca-nss1-retail.bin', src / 'R' / 'retail_router1.bin')

    with open(src / 'README', 'x') as readme:
        readme.write(f"Extracted from {fw.name} on {datetime.datetime.now()}\n")

    tarball = f"{version}.tar.bz2"
    print(f"Creating archive {tarball}\n")
    ret = os.system(f"tar -jvcf {tarball} -C {tmp} {version}")
    if os.waitstatus_to_exitcode(ret) != 0:
        print("Error creating tarball from NSS firmware files")
        exit(os.waitstatus_to_exitcode(ret))

    # Guessing version number
    wifi_tarball = "qca-wifi-fw-QCA9984_hw_1-CNSS.BL.3.0.2-00068-S-1.59256.1.tar.bz2"
    print(f"\nCreating archive {wifi_tarball}")
    ret = os.system(f"tar -jcf {wifi_tarball} -C {libfw} QCA9984")
    if os.waitstatus_to_exitcode(ret) != 0:
        print("Error creating tarball from Wifi firmware files")
        exit(os.waitstatus_to_exitcode(ret))

print(f"\nSuccess!\nPlace {tarball} and {wifi_tarball} into the dl directory")

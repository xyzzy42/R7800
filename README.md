"Voxel" R7800 Firmware
======================

This is based openwrt, but by now it's a really old version.  Netgear releases their
versions for their routers, and they're still updating it.  But Netgear's newest release
has tons of old packages, bugs, and various "things" (AWS IoT, funsjq, ...) that are
better left out.  So Voxel's massively updated and fixed up Netgear firmware.

Except Voxel's source release, which is what this is forked from, doesn't build
with out a bunch of work.

This source repo has stuff to make building it work.  It should be pretty much
the same firmware other than that.

Except Voxel hasn't released the full source to his binary builds, e.g. no
toolchain directory, and the source released isn't always totally up to date, so
it might be a slightly different than the binary.

Getting NSS & Wifi Firmware
---------------------------
To build this you need the firmware for the Atheros Wifi and the Qualcomm NSS
network offload engine, which is not anywhere on the Internet.  Qualcomm wants
to make their hardware as hard to use as possible and won't distribute the
firmware or allow anyone else to do it either.

So you've got to extract it from an existing R7800 image (Netgear or Voxel, same
stuff).

I've written a handy script to do it.  Run `scripts/r7800-nss-fw.py` on a
existing R7800 firmware img file and it will extract the NSS and Wifi files,
detect the NSS version, and create "source" tarballs.  Example:

```
[~/R7800]$ scripts/r7800-nss-fw.py R7800-V1.0.2.93SF.img
Image header detected, fw for R7800 version V1.0.2.93SF
…
…
Creating archive NSS.AK.1.0.c8-00015.tar.bz2
…
Creating archive qca-wifi-fw-QCA9984_hw_1-CNSS.BL.3.0.2-00068-S-1.59256.1.tar.bz2

Success!
Place NSS.AK.1.0.c8-00015.tar.bz2 and qca-wifi-fw-QCA9984_hw_1-CNSS.BL.3.0.2-00068-S-1.59256.1.tar.bz2 into the dl directory

[~/R7800]$ mv NSS.AK.1.0.c8-00015.tar.bz2 qca-wifi-fw-QCA9984_hw_1-CNSS.BL.3.0.2-00068-S-1.59256.1.tar.bz2 dl/
```

You need a recent version of squashfs-tools installed to run this.  The version
that is built as part of this firmware build process is currently too old. 
Maybe someone will update it.


Or if you really want to do it manually:

1. Extract the rootfs.  7zip can do it.
2. Find `/lib/firmware/qca-nss0-retail.bin` and `/lib/firmware/qca-nss1-retail.bin` and extract them from image.
3. Rename them and put them in a directory tree as `NSS.AK.1.0.c8-00015/R/retail_router0.bin` and `NSS.AK.1.0.c8-00015/R/retail_router1.bin`.
4. Make a tarball named `NSS.AK.1.0.c8-00015.tar.bz2` from this, e.g.:  
`tar -jcf NSS.AK.1.0.c8-00015.tar.bz2 NSS.AK.1.0.c8-00015/`
5. Put that tarball in the `dl` directory.

Building
--------
Existing build instructions are out of date.

To build, have a Linux system with the necessary tools installed.  There aren't
very many and they are all common things that any distro should already have
available to install with `dnf`, `apt`, `pacman`, or whatever your distro uses. 

Copy the default R7800 config to to current config with:

```
cp configs/default-r7800 .config
```

Then run make:

```
make
```

That should be it.  It should download all the individual packages and build
everything.

The result will be the file `bin/ipq806x/R7800-Vxxxxx.img`.

Ignore the `compile.sh` script.  It's for one specific person's system and there
is no sense in using it.

Problems Building
-----------------

If it dies why it's in the `"Checking 'something'...  ok."` part at the
beginning of the build, then you are missing some package that you should
install. 

If it's later on that it dies, then it's a good chance it couldn't download the
package.  See above about the "Wifi Firmware", you need to get that yourself!

The last package name printed out, like `make[3] -C toolchain/gdb prepare` or
`make[3] -C package/angular-loadcontent compile` is probably the problem package
(`gdb` and `angular-loadcontent`).  You can probably turn it off it doesn't look
useful to you.  Do this by editing the .config file.  Don't use `make
menuconfig` to do it from the config menu, as that is broken.


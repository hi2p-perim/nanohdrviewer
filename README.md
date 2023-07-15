nanohdrviewer : A simple HDR image viewer
====================

Introduction
--------------------

*nanohdrviewer* is a simple HDR image viewer for Radiance HDR and OpenEXR formats (*.hdr, *.exr).

Features

* Simplicity (one-file python application)
* Draw & drop support
* Automatic reload (useful for preview rendering etc.)

Dependency
--------------------

* Python 3.x
* numpy
* smc.freeimage
* PyQt5


How to run
--------------------
```
$ conda create -n hdrview python=3.10 -y
$ conda activate hdrview
$ pip install imageio PyQt5
$ Python nanohdrviewer.py
```
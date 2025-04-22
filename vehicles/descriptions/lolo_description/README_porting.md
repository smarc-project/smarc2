Lolo Porting progress
=====================

Status
======
Currently just the relevant folders and their contents have been copied.
- launch (See sam_description launch file)
- mesh (?)
- robots (?)
- scripts (This isn't needed anymore)
- urdf (This needs a .urdf <- .urdf.xacro)

These still need to be ported to ROS 2!

TODO
====
[x] Port scripts to Ros 2
[x] Port launch files to Ros 2
[x] Setup CMakeLists.txt
    This might need some tweaking as this is a python package
[x] Setup package.xml
[x] Generate .urdf from .urdf.xacro
[ ] Remove python script stuff
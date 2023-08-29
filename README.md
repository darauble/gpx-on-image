# GPX Track on Image Drawer

This small utility performs a simple task: it draws a GPX track on any image the user provides. It is inspired by old
functionality of Endomondo, which is now long gone.

This utility was generated mostly by ChatGPT, as I, the developer, don't have enough experience with image processing
libraries and GPX workflow. Also, I don't have the experience with GUI, especially working with Python (just some QT
tinkering). However, I still had to add semi-correct coordinates mapping, drawing on the image itself and some more GUI
functionality:

![GPX Track on Image Drawer](screenshot/2023-08-29 09-57-21-gpx-gui-darauble.jpg?raw=true "GPX Track on Image Drawer")

There are some possibilities to make this utility better.

## Coordinate Mapping

Coordinate mapping to the image should take into account the latitute and its effect on proportional distance beteen
longitudinal points. Currently this is not implemented, so GPX tracks nearing equator or poles would get distorted.

## Other Statistics

It would be nice to add track title, average speed/pace, heart rate and anything else, which is deemed worth sharing.
Currently I, myself, share image from Garmin Connect with stats and then additionally put the track on it.

# Slow Glass

Slow Glass is a scripting language to create long-running animations that can respond to external events,
inspired by the famous Bob Shaw short story "The Light of Other Days". It uses Python and Pygame-ce to 
animate a sprite based scene. The expectation is that this scene is displayed continuously as a relaxing
background, perhaps as a continous display running on a Raspberry Pi. The image below is an early prototype
extending a Lego City into the distance with moving cars, trains and varying lighting effects, although
its use is only limited by your imagination and your animation skills!

## The Scripting Language

The aim of the scripting language is to provide a readable, high level description of the scene, the actions
that take place in the scene and the events that trigger them. Hence it is mostly descriptive English with
a minmal number of "programming" constructs. The intention is that a Slow Glass script is both more understandable
and shorter than the equivalent Python / Pygame code would be!

## Basic Concepts

### Image Resources

Putting an image on the screen is a two step process in Slow Glass. First we load an image as a resource and then
define and place one or more sprites that use that image. Images can be static or animated, and other resources
like text and sounds can also be used.

## Sprites

At the simplest, a Sprite is just the content of an image resource placed at a particular point on the screen.
However, Sprites can also be set in motion, scaled, tinted and made transparent, either instantly our gradually
over an extended period of time. Additionally, sprites can display a window onto just a part of their source image
and the window itself can be moved and scaled. If the source image is a movie or a set of sprite animation cells
then each frame can also be displayed under control of the sprite object.

## Scenes

A scene is a small cameo or vignette, so for example a train moving across a scene passing from right to left
accompanied by sound effects and flashing lights on railroad crossing.

## Current State

The program is mostly functionally complete and quite sophisticated effects are possible, however in most
cases an incorrectly writtend script results in an uncaught exception. Additionally, I am still working on:

* Support for GPIO events (Raspberry Pi only)
* Support for movie files as image sources
* Documentation and examples


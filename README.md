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

## Getting Started

### Pre-requisites

Slow Glass is written using Python 3, Pygame-ce(*), Matplotlib, OV and possibly one or two other non-standard
imports that I have forgetton about. For operation on the Raspberry Pi you will also need the GPIO libraries.

### Running Slow Glass

Download the source files from this repository and unpack them somewhere. From the command line go into the
'src' folder and type:

```
python3 -d ../demos/cafe-at-night
```

For your own scripts I think t is simplest to put all your image resources into a folder then put your
Slow Glass script into a file called 'script.txt' in the same folder. Then use the command above, providing
the path to your folder.

### More information

The Wiki https://github.com/karlwilcox/slow-glass/wiki is the best place for a tutorial, example scenes and a
complete reference.

## Basic Concepts

### Image Resources

Putting an image on the screen is a two step process in Slow Glass. First we load an image as a resource and then
define and place one or more sprites that use that image. Images can be static or animated, and other resources
like text and sounds can also be used.

### Sprites

At the simplest, a Sprite is just the content of an image resource placed at a particular point on the screen.
However, Sprites can also be set in motion, scaled, tinted and made transparent, either instantly our gradually
over an extended period of time. Additionally, sprites can display a window onto just a part of their source image
and the window itself can be moved and scaled. If the source image is a movie or a set of sprite animation cells
then each frame can also be displayed under control of the sprite object.

### Scenes

A scene is a small cameo or vignette, so for example a train moving across a scene passing from right to left
accompanied by sound effects and flashing lights on railroad crossing. You can think of a scene as a "package" of
events and actions that can be re-used as required.

### Actions

Most of the Slow Glass scripting language takes the form of commands that carry out actions, placing sprites, moving
them, playing sounds and so on. Actions only happen in response to events. It is also possible to put a condition
on an event such that it will only run if the condition is met.

### Events

Slow Glass supports a wide range of events, commands can be invoked at regular intervals, at particular clock
times, in response to button presses or GPIO events or randomly. An event can trigger any number of actions,
and an action can be invoked by any number of events.

### Variables

Variables are one of the few programming concepts that I have found the need to introduce in Slow Glass. There
are various system variables that give access to things like time, display dimensions and random value. Variables also
give access to characteristics of sprites, their current location, size and so on. Additionally the script
author can define new variables for their own use.

### Expressions

Expressions are the other programming concept needed, although in most cases all that is needed are simple
arithmetic operations and basic comparisons. Should you need it however, (and depending on the configuration
file settings) you can call out to Python itself and get the result of abitrary expressions.

## Contributions

Comments, suggestions, issues and pull requests are welcome! 

## Current State

The program is mostly functionally complete and quite sophisticated effects are possible, however in most
cases an incorrectly writtend script results in an uncaught exception. Additionally, I am still working on:

* Support for GPIO events (Raspberry Pi only)
* Support for movie files as image sources
* Documentation and examples


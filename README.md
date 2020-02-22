READ ME:  Spiraloid Blender 2.79 essentials setup

misc Blender utilities

Unless stated otherwise, many of these scripts and addons are a collaboration of others from the blender open source community. I am posting the python scripts here because as I have updated or modified the code to work with blender 2.79 and suit my own workflows. No warranty or support should be implied. I am merely standing on the shoulders of others.
I try to reference the original authors and link to forum posts or webpages as I can in the history.
Any concerns, feel free to contact me and I can adjust. Just want to share as I get with other awesome blender users.

cheers.

-bay

Installation:

WARNING!!!:  Blender users may wish to backup your current configuration before installing in case something goes wrong you can undo.  For example on a Mac,  creating a compressed zip archive of this folder:

~/Library/Application Support/Blender/2.79

(or on windows 10)

%APPDATA%\Roaming\Blender Foundation\Blender\2.79

 is a good idea.  
(This is where blender stores all your preference data)

Next

Install blender 2.79 (if you have not already done so)
https://www.blender.org/download/releases/2-79/

Open Blender and edit  “file > User Preferences”.
Under the add on tab, use button at Bottom that says “install add on from file”

Browse to this folder where this README.txt file is and install all add-ons in the addon folder as you would normally.

Be sure to activate them immediately after you install them (it’s a long list to search through)

Next

Go to the input tab, use button 
“import key configuration”

Browse to this folder and import “spiraloid_hotkeys.py”

Save user preferences.

Next

Open the startup_scene.blend file in this folder.

If everything went according to plan, everything should be installed.  if everything worked, hit the spacebar and the mirrored subdiv cube in front of you should bounce. 

This is the fast preview playback script I wrote.  Hit spacebar to stop playing time and note that the current frame has returned whatever frame you were editing before you hit spacebar.

CONGRATS!  Everything is installed.  hit “ctrl U” to save the startup scene and all the UI and settings so that every time your launch blender or hit file new, this is what you get.   Home state.

--

Here’s a list of basic usage of my essentials..  Wherever possible I tried to leave it the default so you could still google.  Right Mouse Button (RMB) to select, drag etc.  x to delete.  A to deselect all or Toggle.  GXYZ RXYZ SXYZ alt-S to move on normal etc all still work.

My adjustments to the UI or hotkeys are made for me, so bear in mind I have a lot of habits from using nearly every 3D tool for the last 25 years in major productions.  I understand that the hotkey memorization I do is abnormal, but this kind of configuration helps me switch tools and makes my work faster.



General 3D Navigation:

Alt LMB. orbits the camera.
Alt RMB dolly’s the camera
Alt Shift pans the camera.
(I know I know.  Trust me Maya users, alt shift drag to pan rocks.  But I did put in alt MMB too for the SGI greybeards who like fighting the mouse wheel)

speaking of

Alt shift mouse Wheel dolly’s the camera in and out for 3D and 2D views.  

Mouse wheel over a 3D view and the view will spin around the aimpoint like a sculptors turntable.  If you have a weighted throw mouse wheel like an MX master25 this is amazing.  

You can set the aimpoint by hitting alt-a 
(or cmd-a on a Mac).   This is actually an add-on I had to write.  It moves the cursor and aims to that.  Trust me.  Every other way to do this sucked.

Alt ` set view to current camera
Alt 1 set view to front
Alt 2 set view to left
Alt 3 set view to top
Alt 4 set view to right
Alt 5 set view to bottom
Alt 6 set view to back

Alt mouse wheel scrubs though frames
Cmd mouse wheel scrubs though keyframes of selected objects.

Up Arrow goes to first frame
Down Arrow goes to last frame
Left Arrow goes to next keyframe for selected object.
Right Arrow goes to previous keyframe for selected object.
Alt Right Arrow goes to next frame
Alt Left Arrow goes to previous frame

Ctrl Return does a playblast of whatever window is under your mouse.


WEIGHT PAINT Mode
Ctrl shift Drag will drag a radial gradient of the current weight, tool and strength.
Ctrl ALT Drag will drag a radial gradient of the current weight, tool and strength.

EDIT Mode
E edges
F faces
V vertices


---
---

Addon notes:

(unless the addon states I wrote it, these are grabbed from elsewhere online and copyrtight, support etc stays with the original author.  I'm just collecting them in this repo to have them in once place.  See source code documentation of each addon for more info)

---

MirrorAllVertexGroups.py

this script adds a "Mirror all Vertex Groups" item to the vertex groups menu that will copy all vertex groups from one side of a model to the other for a symmetrical mesh.  this means you can paint weights for the left hand, legs, torso etc and then mirror all weights to the other side (the other side weights are overwritten).  There is a small options menu that comes up to let you choose an axis, copy direction etc.


---

FastPreview.py

This adds a "preview" button to the timeline.  when pressed this will playback (or preview) the current range from the beginning and when pressed again, will return the current frame to the frame before preview.  This is most usefull when refining a pose and wanting to see how it feels in motion without having to constantly place the edit frame over and over again.  When animating, I recommend binding it to the spacebar using view3d.fast_preview (and moving the search to another key, like command+s)
Note: when zoomed into a range in the graph editor, the fast preview will use that range.  view all to play from beginning.

---

AimAtSelected.py

This adds an "Aim Selected" item to the view menu.  This will move the cursor to the selected element and aim the camera at it.  I recomend binding it to alt+a or cmd+a

---

SmoothAnimationLoop.py

This adds a menu to the graph editor > key > smmooth animation loop.  enter the number of frame the falloff should effect and the animation curves at the end of your selected animation will be moved to the values at the start of the animation with a falloff.

---

SimplifyMultipleFCurves-v1_1.py

This adds a menu to the graph editor > properties panel > f-curve > Simplify multiple f-curves > By Error.  the slider to adjust error settings can be found in the 3Dviewport Tool shelf pane.  Adjust the slider to reduce the samples for selected curves.  Works great for creating animator friendly resamples for baked, mocap or puppeteered dense anim curves.

---

JiggleArmature.py

This adds a property to selected bones to simulate physics overlap.  great for floppy, ears, antenae etc etc.  the Jiggle Scene toggle must be set to on in the scene properties to see the results.



---

I also strongly suggest these paid addons:

https://blendermarket.com/products/voxel-heat-diffuse-skinning

https://github.com/ucupumar/yPanel

https://blendermarket.com/products/auto-rig-pro

http://renderhjs.net/textools/blender/

https://gumroad.com/l/uvpackmaster

https://lollypopman.com/2016/08/09/addon-shapekey-helpers/

https://en.blender.org/index.php/Extensions:2.6/Py/Scripts/Animation/Corrective_Shape_Key

https://blendermarket.com/products/asset-management?ref=2

https://github.com/knekke/blender_addons

https://www.blendernation.com/2016/06/15/addon-zaloopok/


---

good luck with your art.

-b

my 3D Graphic Novel "Nanite Fulcrum"
http://spiraloid.net/nanitefulcrum

my patreon
https://www.patreon.com/spiraloid

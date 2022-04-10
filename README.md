
[Walkthrough Video](https://github.com/spiraloid/Spiraloid-Toolkit-for-Blender/blob/master/blender_hotkey_walkthrough.mp4?raw=true)


READ ME:  Spiraloid Blender 3.1 setup

misc Blender utilities

Unless stated otherwise, many of these scripts and addons are a collaboration of others from the blender open source community. I am posting the python scripts here because as I have updated or modified the code to work with blender 3.1 and suit my own workflows. No warranty or support should be implied. I am merely standing on the shoulders of others.
I try to reference the original authors and link to forum posts or webpages as I can in the history.
Any concerns, feel free to contact me and I can adjust. Just want to share as I get with other awesome blender users.

cheers.

-bay

Installation:

WARNING!!!:  Blender users may wish to backup your current configuration before installing in case something goes wrong you can undo.  For example on a Mac,  creating a compressed zip archive of this folder:

~/Library/Application Support/Blender/3.1

(or on windows 10)

%APPDATA%\Roaming\Blender Foundation\Blender\3.1

 is a good idea.  
(This is where blender stores all your preference data)

Next

Install blender 3.1 (if you have not already done so)

https://www.blender.org/download/releases/3-1/

Open Blender with admin priviledges and edit  “edit > User Preferences”.

if you have installed the toolkit on an earlier version of blender, just quite blender, open your %appdata% folder and drag the .py addons from the downloaded zip archive into the scripts/addons folder and overwrite all the old addons, restart blender.

if you are installing for the first time:
Under the addon tab, use button at Bottom that says “install add on from file”

Browse to this folder where this README.txt file is and every *.py file in the addon folder as you would normally.

(Remember to activate each them immediately after you install them, otherwise it’s a long list to search through)

I strongly you buy your own copy of these paid addons as my hotkeys assume they are installed. xray box select especially

https://gumroad.com/l/daldj
https://gum.co/dolly_zoom_truck_shift?recommended_by=library
Next

In the preferences Go to the "Keymap", use the button “import key configuration” and browse to this folder and import “spiraloid_hotkeys.py”

Save user preferences.

Next

Open the startup_scene.blend file in this folder.  (don't touch anything at this point unless you know what you're doing and want the state saved as your startup overriding my startup state. 

hit “ctrl U” and say yes to save the startup scene.  This will store the state of all the UI and settings so that every time your launch blender or hit file new, this is what you get. This is your Home state.

If everything went according to plan, everything should be installed.  if everything worked, hit the spacebar and the mirrored subdiv cube in front of you should bounce. 

This is the fast preview playback script I wrote.  Hit spacebar to stop playing time and note that the current frame has returned whatever frame you were editing before you hit spacebar.

CONGRATS!  Everything is installed. 

checkout this old walkthrough video and look at the hotkey overlay.    


[Walkthrough Video](https://github.com/spiraloid/Spiraloid-Toolkit-for-Blender/blob/master/blender_hotkey_walkthrough.mp4?raw=true)


--

Here’s a list of basic usage of my essentials..  Wherever possible I tried to leave it the blender defaults so googling blender shortcuts and tutorials will still kinda work.  x to delete.  A to deselect all or Toggle.  GXYZ RXYZ SXYZ alt-S to move on normal etc all still work.

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

` toggle between local global pivot placement.  (its called Accent_Grave in the demo video)
Alt ` set view to current camera  (its called Accent_Grave in the demo video)
Alt 1 set view to front
Alt 2 set view to left
Alt 3 set view to top
Alt 4 set view to right
Alt 5 set view to bottom
Alt 6 set view to back

Alt mouse wheel scrubs though frames
Ctrl mouse wheel scrubs though keyframes of selected objects.
Ctrl mouse wheel expands or shrinks selection in edit mode.


Up Arrow goes to first frame
Down Arrow goes to last frame
Left Arrow goes to next keyframe for selected object.
Right Arrow goes to previous keyframe for selected object.
Shift Right Arrow goes to next frame
Shift Left Arrow goes to previous frame

Ctrl Return does a playblast of whatever window is under your mouse.
Ctrl Numpad 0 nukes the selected objects materials and creates a new medium gray material.

in the add object menu (shift+a)  there is now a "Cube Killer" menu item.
this will add a random primitve to the scene.  if something is selected, it will DESTROY the selected object and make the newe primitive fit the size of the destroyed objects.  this is so that you can bind it to a hotkey (like insert) and hit it over and over again, cycling through random primitives.  if no object is selected, the primitive is created at the cursor.  Death to the default Cube!

WEIGHT PAINT Mode
Ctrl shift Drag will drag a radial gradient of the current weight, tool and strength.
Ctrl ALT Drag will drag a radial gradient of the current weight, tool and strength.
X will toggle 0.0 or 1.0 weight

Image Paint mode
X will toggle black or white color

OBJECT mode
w is the tweek tool.  I leave this tool on for everything and use the GRS shortcuts instead of the beginner gizmos.
ctrl+e move origin to cursor
f4 apply all transforms.
alt+D addes a subdivide modifier and two decimat modifiers to the selected objects
D and Shift D for up and down subdivs, if at the max is hit, the decimation modifiers are turned on/off
M will toggle all the modifiers on or off for the visible objects.
shift + right/left arrow will cycle through isolating the visible selected object


EDIT Mode
E toggle edit mode.
double click toggle edit mode
ctrl+enter exit edit mode (handy for lettering)

shift+E Extrude edges/vertices/faces
alt+E selects edge ring
alt+shift+E selects edge ring
ctrl+alt+shift+E selects boundary edge loop

shift+MMB shirnk/fatten selection
ctrl+shift+MMB crease/uncrease edges

q now toggles soft modification  (I got tired of reaching for o)
tab toggles workmode (for render only viewing, too many yeards of muscle memory)
e toggles editmode  (you can still switch modes w ctrl+tab)
D and Shift D for up and down subdivs
alt+D to subdivide selected
S and F wave for bush size.
[ and ] for brush size
ctrl+numpad0 to nuke material/polypaint/texture
ctrl+shift+LMB to lasso mask
alt+ctrl+shift+LMB to lasso mask deselect
ctrl+i invert mask
ctrl+b blur mask
ctrl+h hide mask

SCULPT mode
ctrl+right sets voxel remesh grid size
ctrl+r sets remeshes
ctrl+alt+r uses remeshit from exoside
right drag horizontal adjusts brush size.
right drag vertical adjusts brush opacity.
if you have Quad remesher installed, alt+shift+D will automesh the current model, unwrap and shrink wrap the details onto a multires

POSE mode
shift+r will toggle child lock to parent/world.  handy for FK posing.

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


resize_images.py
obvious

SubdNavigator.py
adds a subdivide modifier to add visile and lets you go up and down resolutions w D and Shift+D

ToggleWeights.py
allows you to use X to switch between 0.0 and 1.0 weighting.  useful for ctrl+shift+drag and ctrl+alt+drag for linear/radial gradient weighting.

Toggle_hide.py
allow H store recall hide toggle to work.

brush_quickset.py
lets the "[" and "]" do brush sizing like photoshop.


---

I also strongly suggest these paid addons:

xray select
https://gumroad.com/l/daldj

dolly zoom
https://gum.co/dolly_zoom_truck_shift?recommended_by=library

Voxel heat diffuse skinning
https://blendermarket.com/products/voxel-heat-diffuse-skinning

https://gumroad.com/l/mfGbS

https://gumroad.com/l/uvpackmaster

https://blendermarket.com/products/auto-rig-pro

http://renderhjs.net/textools/blender/

https://lollypopman.com/2016/08/09/addon-shapekey-helpers/

https://en.blender.org/index.php/Extensions:2.6/Py/Scripts/Animation/Corrective_Shape_Key

https://www.blendernation.com/2016/06/15/addon-zaloopok/

https://gitlab.com/AquaticNightmare/space_switcher/-/wikis/home

---

good luck with your art.


-b

my 3D Comics can be found at:
http://3dcomic.shop



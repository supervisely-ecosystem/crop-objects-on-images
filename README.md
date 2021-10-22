<div align="center" markdown>
<img src="https://i.imgur.com/TslAtO8.png"/>

# Crop objects on images

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a> •
  <a href="#Results">Results</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/crop-objects-on-images)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/crop-objects-on-images)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/crop-objects-on-images&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/crop-objects-on-images&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/crop-objects-on-images&counter=runs&label=runs&123)](https://supervise.ly)

</div>

## Overview

The app crops objects of selected classes in images project and creates a new project. User can define some crop settings - for example, padding, resize and what to do with original labels - keep or ignore. 

Application key points:  
- App works only with the following geometry types: `Bitmap`, `Polygon`, `Rectangle`, `Polyline` (Use another apps to transform class shapes or rasterize objects)

# How To Run 

1. Add [Crop objects on images](https://ecosystem.supervise.ly/apps/crop-objects-on-image) to your team from Ecosystem.

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/crop-objects-on-image" src="https://i.imgur.com/wZiMUWn.png" width="350px" style='padding-bottom: 20px'/>  

2. Run app from the context menu of **Images Project**:

<img src="https://i.imgur.com/cgaP76g.png" width="100%"/>

3. Once app is started, new task appear in workspace tasks. Monitor progress from both "Tasks" list and from application page. To open report in a new tab click "Open" button.
 
<div align="center" markdown>
<img src="https://i.imgur.com/8DemHS7.png"/>
</div>

# How To Use

1. Define settings
2. Press “Preview” button to see results on random image
3. Press “Crop all objects” button to create a new project with cropped objects
4. App shuts down automatically

<div align="center" markdown>
<img src="https://i.imgur.com/r2E6LTe.png"/>
</div>

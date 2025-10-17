<div align="center" markdown>
<img src="https://user-images.githubusercontent.com/48245050/182571801-4c863696-e76f-4e2e-81ec-de6794c257a3.png"/>

# Crop objects on images

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-To-Use">How To Use</a> •
  <a href="#Results">Results</a>
</p>


[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/crop-objects-on-images)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/crop-objects-on-images)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/crop-objects-on-images.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/crop-objects-on-images.png)](https://supervisely.com)

</div>

## Overview

The app crops objects of selected classes in images project and creates a new project. User can define some crop settings - for example, padding, resize, copy object tags to crop images, and what to do with original labels - keep or ignore. 

# How To Run 

1. Add [Crop objects on images](https://ecosystem.supervisely.com/apps/crop-objects-on-image) to your team from Ecosystem.

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/crop-objects-on-image" src="https://i.imgur.com/wZiMUWn.png" width="450px" style='padding-bottom: 20px'/>  

2. Run app from the context menu of **Images Project**:

<img src="https://i.imgur.com/cgaP76g.png" width="100%"/>

3. Once app is started, it will appear in workspace tasks, to open the app click `Open` button
 
<div align="center" markdown>
<img src="https://i.imgur.com/8DemHS7.png"/>
</div>

# How To Use

1. Define settings
2. Press “Preview” button to see results on random image
3. Press “Crop all objects” button to create a new project with cropped objects
4. App shuts down automatically

<div align="center" markdown>
<img src="https://i.imgur.com/AMbQSBB.png"/>
</div>

if checkbox `copy tags to crop` is selected, that every cropped image will have tags that was on corresponding objects:

<div>
  <table>
    <tr style="width: 100%">
      <td>
        <b>Full image</b>
        <img src="https://github.com/supervisely-ecosystem/crop-objects-on-images/releases/download/v0.0.1/full_image.png" style="width:150%;"/>
      </td>
      <td>
        <b>Object crop</b>
        <img src="https://github.com/supervisely-ecosystem/crop-objects-on-images/releases/download/v0.0.1/object_crop.png" style="width:150%;"/>
      </td>
    </tr>
  </table>
</div>

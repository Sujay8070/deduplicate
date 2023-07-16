# kopercep
Offline Perception processing to remove duplicate image frames.

To eliminate similar frames, run the following command in you CLI. 
Provide your local path of images-folder and desired contour area.

```
python main.py -p <image folder path> -a <minimum contour area>

```

A new folder with all "unique" image frames is created inside the provided images-folder.
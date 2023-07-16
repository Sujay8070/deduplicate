# kopercep
Offline Perception processing to remove duplicate image frames.

To eliminate similar frames, run the following command in your CLI. 
Provide your local path of image-folder and the desired contour area.

```
python main.py -p <image folder path> -a <minimum contour area>

```

A new folder with all "unique" image frames is created inside the provided image-folder.
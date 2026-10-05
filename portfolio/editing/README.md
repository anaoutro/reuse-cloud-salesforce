# Editable video source

These MP4s are edited presentations using real Salesforce screenshots and English explanatory titles. They are not continuous screen recordings and contain no audio. Screenshots are unchanged.

Edit `scenes.json` to change titles, durations or screenshot order. On Linux install Python 3, reportlab, DejaVu fonts, FFmpeg and Poppler, then run:

```bash
python portfolio/editing/render_videos.py
```

Outputs are H.264 MP4, 1920x1080, 24 fps. Captions and fade transitions are rendered locally. Keep `render-temp/` out of git.

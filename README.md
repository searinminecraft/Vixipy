<div align="center">
    
![PyXiv logo](/static/pyxiv_wide.png)

# PyXiv

</div>

PyXiv is yet another privacy respecting pixiv frontend, allowing you to enjoy content from pixiv without the tracking. Written in Python using the Flask web framework and other libraries.

This is still in heavy development, so it may take a while before it reaches a stable state.

A mirror of PyXiv can be found on [git.gay](https://git.gay/kita/PyXiv)

# Features currently present
* Built-in proxy (to retrieve illustrations and images from pixiv)
* Log in
* Personalised landing page

# Screenshots

![Screenshot of PyXiv's landing page, logged in as coolesdingdev](/screenshots/screenshot.png)

![Screenshot of an illustration of Anna Yanami, with various information as well as related artworks](/screenshots/artwork.png)

![Screenshot of the discovery page](/screenshots/discover.png)

# Install instructions
1. Create a virtual environment, then activate
```
python -m venv venv
source venv/bin/activate
```

2. Install deps
```
pip install -r requirements.txt
```

3. Open `run.sh` and put in your pixiv account's token to the `PYXIV_TOKEN` variable. See guide from [PixivFE](https://pixivfe-docs.pages.dev/obtaining-pixivfe-token/) for details. You can also configure other settings like port, workers, and Accept-Language header.

4. Finally, execute `run.sh`

PyXiv should now be running on http://localhost:8000

# See also
* [PixivFE](https://codeberg.org/VnPower/PixivFE) - The project I took inspiration from
* [LiteXiv](https://codeberg.org/Peaksol/LiteXiv) - Yet another pixiv frontend, written in PHP

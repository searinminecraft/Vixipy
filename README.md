<div align="center">
    
# Vixipy

</div>

Vixipy is yet another privacy respecting pixiv frontend, allowing you to enjoy content from pixiv without the tracking. Written in Python using the Flask web framework and other libraries.

This is still in heavy development, so it may take a while before it reaches a stable state.

A mirror of Vixipy can be found on [git.gay](https://git.gay/kita/Vixipy)

# Features currently present
* Built-in proxy (to retrieve illustrations and images from pixiv)
* Log in
* Personalised landing page
* Like and bookmark artworks
* Discovery
* View artworks
* Related artworks
* Search tags
* View users (but not their artworks yet)
* Hide/filter out R-18, R-18G and AI generated artworks
* View and post comments/stamps
* View notifications

# Planned features
* Tag search control
* Image proxy caching

<!--
# Screenshots

<details>
<summary>Show screenshots</summary>

![Screenshot of PyXiv's landing page, logged in as coolesdingdev](/screenshots/screenshot.png)

![Screenshot of PyXiv's landing page, showing rankings](/screenshots/home_rankings.png)

![Screenshot of an illustration of Anna Yanami, with various information as well as related artworks](/screenshots/artwork.png)

![Screenshot of the discovery page](/screenshots/discover.png)

![Screenshot of a tag search for "八奈見杏菜 (Anna Yanami)"](/screenshots/tag_search.png)

</details>
-->
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

# Instance List
> If you're interested in hosting a PyXiv instance and want to be here, please [file an issue](https://codeberg.org/vixipy/Vixipy/issues/new).

(none for now. i appreciate if anyone is willing to host one)

## Planned and attempted instances
* ~~adminforge.de~~ denied
* At my house (maybe?)

# See also
* [PixivFE](https://codeberg.org/VnPower/PixivFE) - The project I took inspiration from
* [LiteXiv](https://codeberg.org/Peaksol/LiteXiv) - Yet another pixiv frontend, written in PHP

# License

Vixipy is licensed under the GNU Affero General Public License version 3. You may modify and redistribute PyXiv as long as you comply with the license.

Vixipy comes with NO WARRANTY, and we will certainly not be responsible for anything that happens to your pixiv account (unless its due to a bug on PyXiv that causes account flagging)

<hr>

*pixiv(R) is a registered trademark of pixiv Inc. We are not affiliated with pixiv Inc. in any way.*

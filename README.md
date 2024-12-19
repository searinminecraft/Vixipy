<div align="center">
    
# Vixipy

</div>

Vixipy *[vick-see-pie]* is yet another privacy respecting pixiv frontend, allowing you to enjoy content from pixiv without the tracking. Written in Python using the Flask web framework and other libraries. This is also one of the only frontends that can function mostly without a pixiv token.

This is still in heavy development, so it may take a while before it reaches a stable state.

A mirror of Vixipy can be found on [git.gay](https://git.gay/vixipy/Vixipy)

# Features currently present
* Built-in proxy (to retrieve illustrations and images from pixiv)
* Log in
* Personalised landing page
* Like and bookmark artworks
* Discovery
* View artworks
* Related artworks
* Search tags
* View users (including illustrations, manga, bookmarks, and following users)
* Hide/filter out R-18, R-18G and AI generated artworks
* View and post comments/stamps
* View notifications
* Follow and unfollow users
* Instance administrator can force NSFW off regardless of account settings

# Planned features
* Tag search control
* Image proxy caching

# Screenshots

<details>
<summary>Show screenshots</summary>

![](/screenshots/landing.png)

![](/screenshots/illust.png)

![](/screenshots/user_profile.png)

![](/screenshots/notifications.png)

![](/screenshots/comments.png)

![](/screenshots/emoji.png)

![](/screenshots/bookmarks.png)

![](/screenshots/settings.png)

</details>

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

3. Open `run.sh` and optionally put in your pixiv account's token to the `PYXIV_TOKEN` variable (see guide from [PixivFE](https://pixivfe-docs.pages.dev/obtaining-pixivfe-token/) for details). Using a pixiv account token allows for full access to most features without the user having to log in themselves. You can also configure other settings like port, workers, and Accept-Language header.

> [!WARNING]
> If you specify a pixiv token, you should be ready for situations like pixiv flagging your account and being terminated due to high activity in the server. It is recommended to set up rate limiting on your proxy solution if you can.
>
> There may also be a possibility of pixiv blocking your IP address, but there have been no reported cases of it happening according to other pixiv frontend maintainers and instance admins.

4. Finally, execute `run.sh`

Vixipy should now be running on http://localhost:8000

# Instance List
> If you're interested in hosting a Vixipy instance and want to be here, please [file an issue](https://codeberg.org/vixipy/Vixipy/issues/new).

(none for now. i appreciate if anyone is willing to host one)

## Planned and attempted instances
* ~~adminforge.de~~ denied
* At my house (maybe?)

# Translate Vixipy

<a href="https://translate.codeberg.org/engage/vixipy/">
<img src="https://translate.codeberg.org/widget/vixipy/horizontal-auto.svg" alt="Translation status" />
</a>

If you have the time, [help translate](https://translate.codeberg.org/engage/vixipy/) Vixipy to make it more accessible. No pressure of course.

# See also
* [PixivFE](https://codeberg.org/VnPower/PixivFE) - The project I took inspiration from
* [LiteXiv](https://codeberg.org/Peaksol/LiteXiv) - Yet another pixiv frontend, written in PHP

# License

Vixipy is licensed under the GNU Affero General Public License version 3. You may modify and redistribute Vixipy as long as you comply with the license.

Vixipy comes with NO WARRANTY, and we will certainly not be responsible for anything that happens to your pixiv account.

# Credits

* [Rico040](/ot) for coming up with the awesome name, Vixipy. (To get same result in python: `'pixiv'[::-1] + y`)
* [VnPower](/VnPower) for the awesome PixivFE project
* People who have translated Vixipy:
    * [Myself](/kita) - Filipino `fil`
    * [Peaksol](/Peaksol) - Chinese (Simplified Han Script) `zh_Hans`
    * Maybe you could be in this list? :3

<hr>

*pixiv(R) is a registered trademark of pixiv Inc. This program is not approved, affiliated, or endorsed with pixiv Inc. in any way.*

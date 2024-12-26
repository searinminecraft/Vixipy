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

## Landing
![](/screenshots/landing.png)

## Tag Search
![](/screenshots/tag.png)

## Illustration
![](/screenshots/illust.png)

## Profile
![](/screenshots/user_profile.png)

## Following Users
![](/screenshots/following.png)

## Notifications
![](/screenshots/notifications.png)

## Discover
![](/screenshots/discover.png)

## Comments
![](/screenshots/comments.png)

## Replies
![](/screenshots/reply.png)

## Emoji/Stamp Picker
![](/screenshots/emoji.png)

## Bookmarks
![](/screenshots/bookmarks.png)

## Settings
![](/screenshots/settings.png)

## i18n Demo
![](/screenshots/i18n.png)

## pixivision
![](/screenshots/pixivision.png)

## pixivision Article
![](/screenshots/pixivision_a.png)

*All illustrations are owned by the respective authors. No copyright infringement is intended and is only for fair use and demonstration purposes only. If you want your illustrations here taken down, send mail to [communication@coolesding.unbox.at](mailto:communication@coolesding.unbox.at)*

</details>

<br>

# Install instructions

## Regular method
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

## Docker container
1. Make a copy of the example compose file:
```sh
cp compose.example.yaml compose.yaml
```

Edit the file according to your needs. Read above for details.

2. Run the container as daemon:
```sh
docker compose up -d
```

(use `docker-compose` instead of `docker compose` if that fails)

3. Done

vixipy is listening on 127.0.0.1:8000 by default

# Instance List
> If you're interested in hosting a Vixipy instance and want to be here, please [file an issue](https://codeberg.org/vixipy/Vixipy/issues/new).

* [vx.maid.zone](https://vx.maid.zone)

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

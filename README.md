<div align="center">

![](/screenshots/title.png)

</div>

Vixipy *[vick-see-pie]* is yet another privacy respecting pixiv frontend, allowing you to enjoy content from pixiv without the tracking. Written in Python using the Quart (based on Flask) web framework and other libraries. This is also one of the only frontends that can function mostly without a pixiv token.

A mirror of Vixipy can be found on [git.gay](https://git.gay/vixipy/Vixipy)

# Features currently present
* Built-in proxy (to retrieve illustrations and images from pixiv)
* Log in
* Personalised landing page
* Like and bookmark artworks
* Discovery
* View artworks
* Related artworks
* Search tags (with search options)
* View users (including illustrations, manga, bookmarks, and following users)
* Hide/filter out R-18, R-18G and AI generated artworks
* View and post comments/stamps
* View notifications
* Follow and unfollow users
* Instance administrator can force NSFW off regardless of account settings

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

## Ugoira Conversion and Result

![](/screenshots/ugoira_converting.png)
![](/screenshots/ugoira_result.png)

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

3. Open `run.sh` and configure it to your needs. See below for details

> [!WARNING]
> If you specify a pixiv token, you should be ready for situations like pixiv flagging/terminating your account due to high activity in the server. It is recommended to set up rate limiting on your proxy solution if you can.
>
> There may also be a possibility of pixiv blocking your IP address, but there have been no reported cases of it happening according to other pixiv frontend maintainers and instance admins.

4. Finally, execute `run.sh`

Vixipy should now be running on http://localhost:8000

## Docker container
1. Make a copy of the example compose file:
```sh
cp compose.example.yaml compose.yaml
```

Edit the file according to your needs. See below for details.

2. Run the container as daemon:
```sh
docker compose up -d
```

(use `docker-compose` instead of `docker compose` if that fails)

3. Done

    Vixipy listens on 127.0.0.1:8000 by default

## Configuration

* `PYXIV_PORT`: The port Vixipy will listen to.
* `PYXIV_TOKEN` (optional): pixiv `PHPSESSID` (session token). If not specified, a random one will be used, but
endpoints and features that require authentication will not be accessible unless the user logs in.

    To obtain the `PHPSESSID` cookie, see the instructions [from the PixivFE documentation](https://pixivfe-docs.pages.dev/hosting/obtaining-pixivfe-token/).
* `PYXIV_INSTANCENAME` (default: Vixipy): The name of the instance.
* `PYXIV_NOR18` (default: 0): Disables and hides R-18(G) artworks from being shown and accessed.
* `PYXIV_ACCEPTLANG` (default: en-US,en;q=0.5): The Accept-Language header that will be used for pixiv requests.
* `PYXIV_RATELIMITS` (default: 0): EXPERIMENTAL: Whether to enable rate limiting on the instance (requires [memcached](https://memcached.org/) to be installed)

TODO: find asyncio alternative for pymemcache/memcached wrapper if possible

## Tinkering with the frontend

You can override static files by creating a `pyxiv/instance` folder, and putting your own files there.

For example, you can theme your instance by making `pyxiv/instance/instance.css` file, and putting your rules there.

[Example theme can be found here](https://git.maid.zone/laptop/vixipy-theme/src/branch/main/instance.css)

# Instance List
> If you're interested in hosting a Vixipy instance and want to be here, please [file an issue](https://codeberg.org/vixipy/Vixipy/issues/new?template=.forgejo%2fissue_template%2fnew_instance.yml).

| Name | Address | Onion | Cloudflare? | Country | Notes |
| --- | --- | --- | --- | --- | --- |
| maid.zone | https://vx.maid.zone  | [yes](http://vx.maidzonekwrk4xbbmynqnprq2lu7picruncfscfwmyzbmec6naurhyqd.onion/) | no | DE | |
| NeonW     | http://neonw.su:10353 | no                                                                               | no | KZ | rolling instance and will always be on latest version. Warning: insecure |
| TorVixipy | no                    | [yes](http://mvrlopacpgnjh2rsykqwtwvxkeozzumo7rfy5uawjv4fnm2top5kdqqd.onion/)    | no | UA | | 


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

* [Rico040](https://codeberg.org/ot) for coming up with the awesome name, Vixipy. (To get same result in python: `'pixiv'[::-1] + y`)
* [VnPower](https://codeberg.org/VnPower) for the awesome PixivFE project
* [laptopcat](https://codeberg.org/laptop) for code contributions and ideas
* People who have translated Vixipy:
    * [Myself](https://codeberg.org/kita) (Kita) - Filipino `fil`
    * [Peaksol](https://codeberg.org/Peaksol) - Chinese (Simplified Han Script) `zh_Hans`
    * [divergency](https://codeberg.org/divergency) - Russian `ru`
* Maybe you could be in this list? :3

<hr>

*pixiv(R) is a registered trademark of pixiv Inc. This program is not approved, affiliated, or endorsed with pixiv Inc. in any way.*

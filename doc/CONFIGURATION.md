# Vixipy Configuration

These are all the available options when configuring Vixipy.

Vixipy can be configured by creating `config.py` in the `instance` folder (recommended) or with environment variables with the `VIXIPY_` prefix.

> [!NOTE]
>
> If using environment variables, boolean values should be their integer counterparts (`0 = False`, `1 = True`) and list values should be a string separated with a `,` without a space (example: `Monika,Natsuki,Sayori,Yuri`).

> [!WARNING]
> When using multiple tokens, make sure their settings (region, display settings, etc.) are the same! Otherwise, some issues may occur.

| Name | Description | Type | Default Value |
|-|-|-|-|
| ACCEPT_LANGUAGE | Defines the [`Accept-Language`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Language) header. | string | `en_US,en;q=0.9` |
| BLACKLISTED_TAGS | Defines the tags that are blacklisted. Any works with a tag containing that term will be hidden. | list | [] |
| ACQUIRE_SESSION | Whether to retrieve tokens and certain cookies from pixiv during initialization.<br><br>If disabled, random ones will be generated, but may result in some unforseen issues. | bool | False |
| SECRET_KEY | Defines the secret key used for Flask's flash notifications. Recommended to change for production use. | string | Vyxie |
| INSTANCE_NAME | Defines the instance name. It should be short and memorable. | string | Vixipy |
| LOG_HTTP | Whether to log HTTP requests (not to be confused with `LOG_PIXIV`) | bool | True |
| LOG_PIXIV | Whether to log requests to pixiv servers. If it is disabled, only errors and warnings are logged | bool | True |
| NO_R18 | Whether to disable viewing R-18(G) works instance-wide regardless of server settings.<br><br>Useful when for example your VPS Host's Acceptable Use Policy or ToS disallows such content. | bool | False |
| NO_SENSITIVE | Whether to disable viewing of any sensitive/potentially suggestive works.<br><br>Enabling this will also enable `NO_R18` | bool | False |
| TOKEN | PHPSESSID cookie(s) for authentication with the pixiv API. If none is specified, Vixipy's functionality can be limited unless the user logs in themselves.<br><br>Multiple tokens can be specified.| list or string | [] |
| IMG_PROXY | Specifies the image proxy to use. A list of image proxies can be found [here](https://pixivfe-docs.pages.dev/public-image-proxies/). | string | /proxy/i.pximg.net |
| PIXIV_DIRECT_CONNECTION | Whether to use a direct connection to pixiv servers rather than Cloudflare. Enabling this allows for bypassing blocks (except for Tor exits), but can be slower depending on network conditions and physical location of the device or server. | bool | False |
| CACHE_PIXIV_REQUESTS | Whether to cache requests from pixiv. If disabled, all requests to pixiv will be sent directly without caching. Anything that dynamically changes (e.g. discovery and landing page when logged in) will not be cached.<br><br>(Requires [Memcached](https://www.memcached.org)) | bool | False |
| CACHE_TTL | This is the duration in seconds for which an item remains valid in the cache before it's considered stale and needs to be fetched again from the pixiv API.<br><br>The TTL is applied to most API responses and can safely be set to a high value. Dynamic content such as Discovery and Newest is never cached. | integer | 300 |
| MEMCACHED_HOST | Host/address for Memcached | string | 127.0.0.1 |
| MEMCACHED_PORT | Port for Memcached | 1-65535 | 11211 |
| ADDITIONAL_THEMES | Defines additional themes user can pick in the settings menu.<br><br>They can be placed on the `instance/custom/themes` folder. | list | None |
| DEFAULT_THEME | Defines the default theme if user has not set a theme yet. If a custom theme, it must be available in the `ADDITIONAL_THEMES` | string | None |
| QUART_RATE_LIMITER_ENABLED | Whether to enable the rate limiter (requires Memcached) | bool | False |
| BEHIND_REVERSE_PROXY | Gives a hint to Vixipy whether it's behind a reverse proxy (e.g. Nginx, Caddy) | bool | False |
| COMPRESS_RESPONSE | Whether to compress response data. If your reverse proxy already does this, you can disable it. | bool | True |
| UGOIRA_ENDPOINT | Determines the Ugoira proxy to use. `%s` denotes where the ID will be placed <br><br>When using [simple-webm-ugoira](https://gitlab.com/pixivfe/simple-webm-ugoira), **make sure** to set the format to a video format! (Example: `http://localhost:8080/ugoira/%s?format=webm`) | string | `https://t-hk.ugoira.com/ugoira/%s.mp4` |
| UGOIRA_REFERER | Determines the `Referer` header for Ugoira proxy. Useful if for example the endpoint is only limited to certain referrers (like ugoira.com) | string | `https://ugoira.com` |


###### Parts of this documentation are derived from the [PixivFE Documentation](https://pixivfe-docs.pages.dev) and are licensed under the GFDL-1.3-or-later.

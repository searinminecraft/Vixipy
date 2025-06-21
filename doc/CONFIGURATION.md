# Vixipy Configuration

These are all the available options when configuring Vixipy.

Vixipy can be configured by creating `config.py` in the `instance` folder (recommended) or with environment variables with the `VIXIPY_` prefix.

> ![NOTE]
>
> If using environment variables, boolean values should be their integer counterparts (`0 = False`, `1 = True`) and list values should be a string separated with a `,` without a space (example: `Monika,Natsuki,Sayori,Yuri`).

| Name | Description | Type | Default Value |
|-|-|-|-|
| ACCEPT_LANGUAGE | Defines the [`Accept-Language`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Language) header. | string | `en_US,en;q=0.9` |
| SECRET_KEY | Defines the secret key used for Flask's flash notifications. Recommended to change for production use. | string | Vyxie |
| INSTANCE_NAME | Defines the instance name. It should be short and memorable. | string | Vixipy |
| LOG_HTTP | Whether to log HTTP requests (not to be confused with `LOG_PIXIV`) | bool | True |
| LOG_PIXIV | Whether to log requests to pixiv servers. If it is disabled, only errors and warnings are logged | bool | True |
| NO_R18 | Whether to disable viewing R-18(G) works instance-wide regardless of server settings.<br><br>Useful when for example your VPS' Acceptable Use Policy disallows such content. | bool | False |
| NO_SENSITIVE | Whether to disable viewing of any sensitive/potentially suggestive works.<br><br>Enabling this will also enable `NO_R18` | bool | False |
| TOKEN | PHPSESSID cookie(s) for authentication with the pixiv API. If none is specified, Vixipy's functionality can be limited unless the user logs in themselves.<br><br>Multiple tokens can be specified.| list or string | [] |
| IMG_PROXY | Specifies the image proxy to use. A list of image proxies can be found [here](https://pixivfe-docs.pages.dev/public-image-proxies/). | string | /proxy/i.pximg.net |
| PIXIV_DIRECT_CONNECTION | Whether to use a direct connection to pixiv servers rather than Cloudflare. Enabling this allows for bypassing blocks (except for Tor exits), but can be slower depending on network conditions and location. | bool | False |
| CACHE_PIXIV_REQUESTS | Whether to cache requests from pixiv. If disabled, all requests to pixiv will be sent directly without caching. <br><br>Note: This requires [Memcached](https://www.memcached.org), and requires the `-I` argument to be set to at least `4m`. | bool | False |
| CACHE_TTL | This is the duration in seconds for which an item remains valid in the cache before it's considered stale and needs to be fetched again from the pixiv API.<br><br>The TTL is applied to most API responses and can safely be set to a high value. Dynamic content such as Discovery and Newest is never cached. | integer | 300 |
| MEMCACHED_HOST | Host/address for Memcached | string | 127.0.0.1 |
| MEMCACHED_PORT | Port for Memcached | 1023-65535 | 11211 |


###### Parts of this documentation are derived from the [PixivFE Documentation](https://pixivfe-docs.pages.dev) and are licensed under the GFDL-1.3-or-later.
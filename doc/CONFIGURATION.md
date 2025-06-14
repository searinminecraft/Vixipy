# Vixipy Configuration

Vixipy can be configured by using environment variables, all starting with `VIXIPY_`.

* `ACCEPT_LANGUAGE`: (Default: `en_US,en;q=0.9`) Defines the [`Accept-Language`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Language) header.
* `SECRET_KEY`: (Default: `Vyxie`) Defines the secret key used for Flask's flash notifications. Recommended to change for production use.
* `INSTANCE_NAME`: (Default: `Vixipy`) Defines the instance name.
* `LOG_HTTP`: (Default: 1) Whether to log HTTP requests (does not affect pixiv reqtests)
* `LOG_PIXIV`: (Default: 1) Whether to log requests to pixiv. If turned off, only errors are logged
* `NO_R18`: (Default: 0) Whether to disable R-18 work viewing
* `NO_SENSITIVE`: (Default: 0) Whether to disable Sensitive works. Enabling this will also enable `NO_R18`
* `TOKEN`: The pixiv token to use for all unauthenticated requests. If not specified, a random one will be used, and all endpoints that require authentication will require login.
    * You can specify multiple tokens by separating them with a `,`. Vixipy will choose a random one for each request context.
* `IMG_PROXY`: (Default: `/proxy/i.pximg.net`) Specifies the image proxy to use. A list of image proxies can be found [here](https://pixivfe-docs.pages.dev/public-image-proxies/).
* `PIXIV_DIRECT_CONNECTION`: (Default: 0) Whether to use a direct connection to pixiv servers rather than Cloudflare. Enabling this allows for bypassing blocks (except for Tor exits), but can be slower depending on network conditions and location.
* `CACHE_PIXIV_REQUESTS`: (Default: 0) Whether to cache requests from pixiv. If disabled, all requests to pixiv will be sent directly without caching.
    * Note: This requires [Memcached]("https://www.memcached.org"), and requires the `-I` argument to be set to at least `4m`.
* `CACHE_TTL`: (Default: 300) This is the duration in seconds for which an item remains valid in the cache before it's considered stale and needs to be fetched again from the pixiv API.
    * The TTL is applied to most API responses and can safely be set to a high value. Dynamic content such as Discovery and Newest is never cached.
* `MEMCACHED_HOST`: (Default: `127.0.0.1`) Specifies the Memcached host
* `MEMCACHED_PORT`: (Default: 11211) Specifies the Memcached port

###### Parts of this documentation are derived from the [PixivFE Documentation](https://pixivfe-docs.pages.dev) and are licensed under the GFDL-1.3-or-later.
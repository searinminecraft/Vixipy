# Vixipy Configuration

Vixipy can be configured by using environment variables, all starting with `VIXIPY_`.

* `ACCEPT_LANGUAGE`: (Default: `en_US,en;q=0.9`) Defines the [`Accept-Language`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Accept-Language) header.
* `SECRET_KEY`: (Default: `Vyxie`) Defines the secret key used for Flask's flash notifications. Recommended to change for production use.
* `INSTANCE_NAME`: (Default: `Vixipy`) Defines the instance name.
* `LOG_HTTP`: (Default: 1) Whether to log HTTP requests (does not affect pixiv reqtests)
* `NO_R18`: (Default: 0) Whether to disable R-18 work viewing
* `NO_SENSITIVE`: (Default: 0) Whether to disable Sensitive works. Enabling this will also enable `NO_R18`
* `TOKEN`: The pixiv token to use for all unauthenticated requests. If not specified, a random one will be used, and all endpoints that require authentication will require login.
    * You can specify multiple tokens by separating them with a `,`. Vixipy will choose a random one for each request context.
* `IMG_PROXY`: (Default: `/proxy/i.pximg.net`) Specifies the image proxy to use. A list of image proxies can be found [here](https://pixivfe-docs.pages.dev/public-image-proxies/).
* `PIXIV_DIRECT_CONNECTION`: (Default: 0) Whether to use a direct connection to pixiv servers rather than Cloudflare. Enabling this allows for bypassing blocks (except for Tor exits), but can be slower depending on network conditions and location.

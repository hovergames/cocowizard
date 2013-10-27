# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sh
from path import path
from PIL import Image

from ..utils import config
from ..utils.log import debug, error, indent

def run():
    stores = config.get("icons")
    if not stores:
        error("Please configure all stores / icon configurations first")

    input_dir = path("Meta/icons")
    output_dir = path("Meta/_generated")

    try:
        icon = Image.open(input_dir / "icon.png").convert("RGBA")
        mask = Image.open(input_dir / "mask.png").convert("L")
        overlay = Image.open(input_dir / "overlay.png").convert("RGBA")
    except BaseException as e:
        debug(e)
        error("Unable to load all required icon files")

    icon_mask = Image.new("RGBA", icon.size)
    icon_mask.paste(icon, mask=mask)
    icon_overlay = icon.copy()
    icon_overlay.paste(overlay, mask=overlay)
    icon_overlay_mask = Image.new("RGBA", icon_overlay.size)
    icon_overlay_mask.paste(icon_overlay, mask=mask)

    for store in stores:
        store_dir = output_dir / str(store)
        if not store_dir.exists():
            store_dir.makedirs_p()

        overlay = stores[store]["settings"]["overlay"]
        mask = stores[store]["settings"]["mask"]

        for size, ext in stores[store]["sizes"].items():
            ext = ext.lower()
            if overlay:
                if mask and ext == "png":
                    store_icon = icon_overlay_mask
                else:
                    store_icon = icon_overlay
            else:
                if mask and ext == "png":
                    store_icon = icon_mask
                else:
                    store_icon = icon

            name = store_dir / "icon-%s.%s" % (size, ext)
            debug("create: %s" % name)

            store_icon = store_icon.resize((size, size), Image.ANTIALIAS)
            store_icon.save(name, ext, quality=100, optimize=True, progressive=True)

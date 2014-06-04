# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from PIL import Image

from ..utils import config
from ..utils.log import debug, error

def run():
    stores = config.get("icons")
    if not stores:
        error("Please configure all stores / icon configurations first")

    input_dir = path("Meta/icons")
    output_dir = path("Meta/_generated")
    output_dir.makedirs_p()

    icon_file = input_dir / "icon.png"
    mask_file = input_dir / "mask.png"
    overlay_file = input_dir / "overlay.png"

    old_files = list(output_dir.walkfiles())
    if len(old_files) > 0:
        src_time = max(icon_file.mtime, mask_file.mtime, overlay_file.mtime)
        dst_time = min(map(lambda x: x.mtime, old_files))
        if src_time < dst_time:
            debug("Generated icons seem to be up to date")
            return

    try:
        icon = Image.open(icon_file).convert("RGBA")
        mask = Image.open(mask_file).convert("L")
        overlay = Image.open(overlay_file).convert("RGBA")
    except BaseException as e:
        debug(e)
        error("Unable to load all required icon files")

    icon_mask = Image.new("RGBA", icon.size)
    icon_mask.paste(icon, mask=mask)
    icon_overlay = icon.copy()
    icon_overlay.paste(overlay, mask=overlay)
    icon_overlay_mask = Image.new("RGBA", icon_overlay.size)
    icon_overlay_mask.paste(icon_overlay, mask=mask)

    for store_name, store in stores.items():
        store_dir = output_dir / store_name
        if not store_dir.exists():
            store_dir.makedirs_p()

        overlay = store["overlay"]
        mask = store["mask"]

        for ext, sizes in store["sizes"].items():
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

            for size in sizes:
                filename = store_dir / "icon-%s.%s" % (size, ext)
                debug("create: %s" % filename)

                store_icon = store_icon.resize((size, size), Image.ANTIALIAS)
                store_icon.save(filename, ext, quality=100, optimize=True, progressive=True)

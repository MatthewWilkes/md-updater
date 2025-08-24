import asyncio

from events.input import Button, BUTTON_TYPES, ButtonDownEvent, ButtonUpEvent
from system.eventbus import eventbus
from tildagonos import tildagonos
from app_components import tokens, layout
import app
import time
from machine import I2C
from system.hexpansion.util import (
    read_hexpansion_header,
    get_hexpansion_block_devices,
    detect_eeprom_addr,
)
from system.notification.events import ShowNotificationEvent
from system.hexpansion.events import HexpansionInsertionEvent
import vfs
import os


class Fixer(app.App):

    def __init__(self, config=None):
        super().__init__()
        self.config = config
        eventbus.on_async(
            HexpansionInsertionEvent, self.handle_hexpansion_insertion, self
        )
        self.status = "Insert MD Interface hexpansion"

    async def handle_hexpansion_insertion(self, event):
        await asyncio.sleep(1)
        
        i2c = I2C(event.port)

        # Autodetect eeprom addr
        addr, addr_len = detect_eeprom_addr(i2c)
        if addr is None:
            print("Scan found no eeproms")
            return

        # Do we have a header?
        header = read_hexpansion_header(i2c, addr)
        if header is None:
            return

        if header.vid == 0xCAFE and header.pid == 0x5E6A:
            # This is ours
            print("Found")
            self.status = f"Found {header.friendly_name} #{header.unique_id}"
            await asyncio.sleep(0.5)
            
            # Try creating block devices, one for the whole eeprom,
            # one for the partition with the filesystem on it
            try:
                eep, partition = get_hexpansion_block_devices(i2c, header, addr)
            except RuntimeError as e:
                return
            
            mountpoint = '/fixingsega'
            vfs.mount(partition, mountpoint, readonly=False)
            print(os.listdir(mountpoint))
            
            self.status = "Mounted filesystem"
            await asyncio.sleep(0.5)
            print("1")
            path = "/" + __file__.rsplit("/", 1)[0] + "/sega.py"
            print("2")
            with open(f"{mountpoint}/app.py", "wt") as appfile:
                print("3")
                with open(path, "rt") as template:
                    print("4")
                    appfile.write(template.read())
            self.status = "Updated application"
            vfs.umount(mountpoint)
            await asyncio.sleep(3)
            self.status = ""
            self.minimise()


    def update(self, delta=None):
        pass
    
    def draw(self, ctx):
        tokens.clear_background(ctx)
        ctx.move_to(0,0)
        ctx.font_size = 12
        ctx.text_align = ctx.CENTER
        ctx.rgb(1, 1, 1)
        ctx.text(self.status)
        
__app_export__ = Fixer
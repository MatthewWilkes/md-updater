import asyncio

from events.input import Button, BUTTON_TYPES, ButtonDownEvent, ButtonUpEvent
from system.eventbus import eventbus
from tildagonos import tildagonos
from app_components import tokens, layout
import app
import time


BUTTONS = {
    "UP": Button("UP", "SegaController", BUTTON_TYPES["UP"]),
    "DOWN": Button("DOWN", "SegaController", BUTTON_TYPES["DOWN"]),
    "LEFT": Button("LEFT", "SegaController", BUTTON_TYPES["LEFT"]),
    "RIGHT": Button("RIGHT", "SegaController", BUTTON_TYPES["RIGHT"]),
    "A": Button("A", "SegaController"),
    "B": Button("B", "SegaController", BUTTON_TYPES["CANCEL"]),
    "C": Button("C", "SegaController"),
    "X": Button("D", "SegaController"),
    "Y": Button("E", "SegaController"),
    "Z": Button("F", "SegaController"),
    "START": Button("START", "SegaController", BUTTON_TYPES["CONFIRM"]),
    "MODE": Button("MODE", "SegaController"),
}


class Sega(app.App):

    def __init__(self, config=None):
        self.config = config

    def update(self, delta=None):
        self.minimise()
    
    async def background_task(self):
        self.button_states = button_states = {}
        while 1:
            last_states = {button: value for (button, value) in button_states.items()}
            three_button = False
            six_button = False
            last = time.ticks_us()
            for i, state in enumerate([1, 0, 1, 0, 1]):
                last = time.ticks_us()
                self.config.pin[1].value(state)
                if i == 2:
                    # Read 2 button controls
                    button_states['UP'] = not self.config.ls_pin[0].value(read=True) 
                    button_states['DOWN'] = not self.config.ls_pin[1].value(read=False)
                    button_states['LEFT'] = not self.config.ls_pin[2].value(read=False) 
                    button_states['RIGHT'] = not self.config.ls_pin[3].value(read=False) 
                    button_states['B'] = not self.config.ls_pin[4].value(read=False) 
                    button_states['C'] = not self.config.pin[0].value()
                if i == 3:
                    # Read 3 button controls
                    button_states['A'] = not self.config.ls_pin[4].value(read=True)
                    button_states['START'] = not self.config.pin[0].value()

            for button, value in button_states.items():
                if value and not last_states.get(button):
                    await eventbus.emit_async(ButtonDownEvent(button=BUTTONS[button]))
                if not value and last_states.get(button):
                    await eventbus.emit_async(ButtonUpEvent(button=BUTTONS[button]))
                
            await asyncio.sleep(0.05)
            
__app_export__ = Sega
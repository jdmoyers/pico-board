import board
from digitalio import DigitalInOut, Direction, Pull
import time
import usb_midi
import adafruit_midi

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


def get_velocity(input_value):
    input_min = 0.0019
    input_max = 0.25
    output_min = 127
    output_max = 1
    input_value = min(max(input_value, input_min), input_max)
    input_range = input_max - input_min
    output_range = output_max - output_min
    mapped_value = (input_value - input_min) / input_range * output_range + output_min

    return int(mapped_value)


key_mappings = [
    {"key": "f2", "row": 2, "col_start": 9, "col_end": 8, "note": 41},
    {"key": "f#2", "row": 2, "col_start": 6, "col_end": 7, "note": 42},
    {"key": "g2", "row": 1, "col_start": 5, "col_end": 4, "note": 43},
    {"key": "g#2", "row": 1, "col_start": 2, "col_end": 3, "note": 44},
    {"key": "a2", "row": 1, "col_start": 1, "col_end": 0, "note": 45},
    {"key": "a#2", "row": 1, "col_start": 10, "col_end": 11, "note": 46},
    {"key": "b2", "row": 1, "col_start": 9, "col_end": 8, "note": 47},
    {"key": "c3", "row": 1, "col_start": 6, "col_end": 7, "note": 48},
    {"key": "c#3", "row": 0, "col_start": 5, "col_end": 4, "note": 49},
    {"key": "d3", "row": 0, "col_start": 2, "col_end": 3, "note": 50},
    {"key": "d#3", "row": 0, "col_start": 1, "col_end": 0, "note": 51},
    {"key": "e3", "row": 0, "col_start": 10, "col_end": 11, "note": 52},
    {"key": "f3", "row": 0, "col_start": 9, "col_end": 8, "note": 53},
    {"key": "f#3", "row": 0, "col_start": 6, "col_end": 7, "note": 54},
    {"key": "g3", "row": 3, "col_start": 5, "col_end": 4, "note": 55},
    {"key": "g#3", "row": 3, "col_start": 2, "col_end": 3, "note": 56},
    {"key": "a3", "row": 3, "col_start": 1, "col_end": 0, "note": 57},
    {"key": "a#3", "row": 3, "col_start": 10, "col_end": 11, "note": 58},
    {"key": "b3", "row": 3, "col_start": 9, "col_end": 8, "note": 59},
    {"key": "c4", "row": 3, "col_start": 6, "col_end": 7, "note": 60},
    {"key": "c#4", "row": 4, "col_start": 5, "col_end": 4, "note": 61},
    {"key": "d4", "row": 4, "col_start": 2, "col_end": 3, "note": 62},
    {"key": "d#4", "row": 4, "col_start": 1, "col_end": 0, "note": 63},
    {"key": "e4", "row": 4, "col_start": 10, "col_end": 11, "note": 64},
    {"key": "f4", "row": 4, "col_start": 9, "col_end": 8, "note": 65},
    {"key": "f#4", "row": 4, "col_start": 6, "col_end": 7, "note": 66},
    {"key": "g4", "row": 5, "col_start": 5, "col_end": 4, "note": 67},
    {"key": "g#4", "row": 5, "col_start": 2, "col_end": 3, "note": 68},
    {"key": "a4", "row": 5, "col_start": 1, "col_end": 0, "note": 69},
    {"key": "a#4", "row": 5, "col_start": 10, "col_end": 11, "note": 70},
    {"key": "b4", "row": 5, "col_start": 9, "col_end": 8, "note": 71},
    {"key": "c5", "row": 5, "col_start": 6, "col_end": 7, "note": 72},
]

row_pins = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5]
col_pins = [
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
    board.GP16,
    board.GP17,
]

rows = [DigitalInOut(pin) for pin in row_pins]
cols = [DigitalInOut(pin) for pin in col_pins]

key_states = {key["key"]: 0 for key in key_mappings}
key_times = {key["key"]: 0 for key in key_mappings}

for row in rows:
    row.direction = Direction.OUTPUT
    row.value = True

for col in cols:
    col.direction = Direction.INPUT
    col.pull = Pull.UP

while True:
    for row_idx, row in enumerate(rows):
        row.value = False

        for col_idx, col in enumerate(cols):
            key_mapping = None

            for km in key_mappings:
                event_type = 0
                if km["row"] == row_idx and km["col_start"] == col_idx:
                    key_mapping = km
                    event_type = 1
                    break

                if km["row"] == row_idx and km["col_end"] == col_idx:
                    key_mapping = km
                    event_type = 2
                    break

            if key_mapping:
                key = key_mapping["key"]
                note = key_mapping["note"]

                if not col.value:
                    if event_type == 1 and key_states[key] == 0:
                        col_start_time = time.monotonic()
                        key_states[key] = 1
                        key_times[key] = col_start_time

                    if event_type == 2 and key_states[key] == 1:
                        key_states[key] = 2
                        col_end_time = time.monotonic()
                        velocity = col_end_time - key_times[key]
                        key_velocity = get_velocity(velocity)
                        midi.send(NoteOn(note, key_velocity))
                        print(f"Input Velocity: {velocity}, Calculated: {key_velocity}")

                else:
                    if key_states[key] == 2:
                        key_states[key] = 0
                        key_times[key] = 0
                        midi.send(NoteOff(note, 0))
                    if event_type == 1 and key_states[key] == 1:
                        key_states[key] = 0
                        key_times[key] = 0

        row.value = True

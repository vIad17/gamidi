# AKAI_Fire_RGB_Controller/hardware/akai_fire_controller.py
import mido
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import math 

FIRE_BUTTON_PLAY = 0x33
FIRE_BUTTON_STOP = 0x34
FIRE_BUTTON_REC = 0x35
FIRE_BUTTON_STEP = 0x2C
FIRE_BUTTON_NOTE = 0x2D
FIRE_BUTTON_DRUM = 0x2E 
FIRE_BUTTON_PERFORM = 0x2F 
FIRE_BUTTON_SHIFT = 0x30
FIRE_BUTTON_ALT = 0x31
FIRE_BUTTON_PATTERN_SONG = 0x32
FIRE_BUTTON_PATTERN_UP = 0x1F
FIRE_BUTTON_PATTERN_DOWN = 0x20
FIRE_BUTTON_BROWSER = 0x21
FIRE_BUTTON_GRID_LEFT = 0x22
FIRE_BUTTON_GRID_RIGHT = 0x23
FIRE_BUTTON_BANK = 0x1A
FIRE_BUTTON_SELECT = 25

FIRE_BUTTON_MUTE_FIRST = 36
FIRE_BUTTON_PAD_FIRST = 54

FIRE_KNOB_FIRST = 16
FIRE_KNOB_SELECT = 118

LED_PRESETS = 27

LED_OFF = 0x00
LED_SINGLE_COLOR_DULL = 0x01
LED_SINGLE_COLOR_HIGH = 0x02
LED_DUAL_COLOR_YELLOW_DULL = 0x01
LED_DUAL_COLOR_SECONDARY_DULL = 0x02
LED_DUAL_COLOR_YELLOW_HIGH = 0x03
LED_DUAL_COLOR_SECONDARY_HIGH = 0x04
LED_PLAY_GREEN_HIGH = LED_SINGLE_COLOR_HIGH
LED_STOP_RED_HIGH = LED_SINGLE_COLOR_HIGH
BANK_LED_CC = 0x1B
BANK_LED_VALUE_ALL_OFF = 0x10

class MidiInputThread(QThread):
    message_received = pyqtSignal(object)
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.in_port = None
        self._running = False
        self.setObjectName(f"MidiInputThread_{port_name.replace(' ', '_')}")

    def run(self):
        self._running = True
        try:
            if self.in_port and not self.in_port.closed: self.in_port.close()
            with mido.open_input(self.port_name) as self.in_port:
                print(f"MidiInputThread ({self.objectName()}): Successfully opened port '{self.port_name}'")
                while self._running:
                    for msg in self.in_port.iter_pending():
                        # print(f"MIDI INPUT THREAD ({self.objectName()}) RAW MSG: {msg}")  # Debug print
                        self.message_received.emit(msg)
                    self.msleep(10)
        except Exception as e: print(f"MidiInputThread: Error for '{self.port_name}': {e}")
        finally:
            if self.in_port and not self.in_port.closed: self.in_port.close()
            self._running = False
            print(f"MidiInputThread: Stopped for port '{self.port_name}'")

    def stop(self): self._running = False

class AkaiFireController(QObject):
    fire_button_event = pyqtSignal(int, bool)
    control_change_event = pyqtSignal(int, int) # control_cc, value

    rec_button_event = pyqtSignal(bool)
    stop_button_event = pyqtSignal(bool)
    play_button_event = pyqtSignal(bool)
    metronome_button_event = pyqtSignal(bool)

    alt_button_event = pyqtSignal(bool)
    shift_button_event = pyqtSignal(bool)
    perform_button_event = pyqtSignal(bool)
    drum_button_event = pyqtSignal(bool)
    note_button_event = pyqtSignal(bool)
    step_button_event = pyqtSignal(bool)
    buttom_row_buttons_event = pyqtSignal(bool, int)

    pattern_button_event = pyqtSignal(bool, int)
    browser_button_event = pyqtSignal(bool)
    select_button_event = pyqtSignal(bool)
    grid_button_event = pyqtSignal(bool, int)

    bank_button_event = pyqtSignal(bool)

    mute_button_event = pyqtSignal(bool, int)
    pad_button_event = pyqtSignal(bool, int, int)

    def __init__(self, default_port_name_to_try: str | None = None, auto_connect: bool = True):
        super().__init__()
        self.out_port = None
        self.port_name_used = None
        self.in_port_name_used = None
        self.midi_input_thread: MidiInputThread | None = None
        self.current_brightness_factor: float = 1.0 # 0.0 to 1.0
        self.NON_GRID_BUTTON_CCS = [
            FIRE_BUTTON_STEP, FIRE_BUTTON_NOTE, FIRE_BUTTON_DRUM, FIRE_BUTTON_PERFORM,
            FIRE_BUTTON_SHIFT, FIRE_BUTTON_ALT, FIRE_BUTTON_PATTERN_SONG,
            FIRE_BUTTON_PLAY, FIRE_BUTTON_STOP, FIRE_BUTTON_REC,
            FIRE_BUTTON_PATTERN_UP, FIRE_BUTTON_PATTERN_DOWN,
            FIRE_BUTTON_BROWSER, FIRE_BUTTON_GRID_LEFT, FIRE_BUTTON_GRID_RIGHT,
            FIRE_BUTTON_BANK, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B
        ]
        self.BANK_LED_CC = BANK_LED_CC 
        self.BANK_LED_OFF_VALUE = BANK_LED_VALUE_ALL_OFF
        if auto_connect:
            port_to_connect = default_port_name_to_try
            if not port_to_connect:
                available_ports = self.get_available_output_ports()
                fire_ports = [p for p in available_ports if ('fire' in p.lower() or 'akai' in p.lower()) and 'midiin' not in p.lower()]
                if fire_ports: port_to_connect = fire_ports[0]
                else: print("AkaiFireController: Auto-connect: No 'Fire' output found.")
            if port_to_connect:
                try:
                    self.out_port = mido.open_output(port_to_connect)
                    self.port_name_used = port_to_connect
                    print(f"AkaiFireController: Auto-connected OUTPUT to: {self.port_name_used}")
                    self._initialize_device_leds()
                except Exception as e:
                    print(f"AkaiFireController: Error auto-connecting OUTPUT '{port_to_connect}': {e}")
                    self.out_port = None; self.port_name_used = None
        else: print("AkaiFireController: Initialized (auto-connect=False).")

    @staticmethod
    def get_available_output_ports():
        try: return mido.get_output_names()
        except Exception as e: print(f"AkaiFireController: Error MIDI outputs: {e}"); return []

    @staticmethod
    def get_available_input_ports():
        try: return mido.get_input_names()
        except Exception as e: print(f"AkaiFireController: Error MIDI inputs: {e}"); return []

    def connect(self, out_port_name: str, in_port_name: str | None = None) -> bool:
        if self.is_connected(): print(f"Output already on {self.port_name_used}. Disconnect first."); return False
        try:
            self.out_port = mido.open_output(out_port_name)
            self.port_name_used = out_port_name
            print(f"AkaiFireController: Connected OUTPUT to: {out_port_name}")
            self._initialize_device_leds()
            if in_port_name and in_port_name not in ["No MIDI input ports found", "Select MIDI Input", ""]:
                self.connect_input(in_port_name)
            return True
        except Exception as e:
            print(f"AkaiFireController: Error connecting OUTPUT '{out_port_name}': {e}")
            self.out_port = None; self.port_name_used = None; return False

    def connect_input(self, port_name: str) -> bool:
        if self.midi_input_thread and self.midi_input_thread.isRunning():
            if self.in_port_name_used == port_name: return True 
            else: self.disconnect_input()
        self.in_port_name_used = port_name
        self.midi_input_thread = MidiInputThread(port_name, parent=self)
        self.midi_input_thread.message_received.connect(self._parse_midi_message)
        self.midi_input_thread.start()
        return self.midi_input_thread.isRunning()

    def disconnect(self):
        if self.out_port:
            print(f"AkaiFireController: Disconnecting OUTPUT from {self.port_name_used}...")
            self._initialize_device_leds(); time.sleep(0.05) 
            try: self.out_port.close()
            except Exception as e: print(f"AkaiFireController: Error closing output port: {e}")
            self.out_port = None; self.port_name_used = None
            print("AkaiFireController: AKAI Fire OUTPUT closed.")
        self.disconnect_input()

    def disconnect_input(self):
        if self.midi_input_thread:
            if self.midi_input_thread.isRunning():
                self.midi_input_thread.stop()
                if not self.midi_input_thread.wait(1000):
                    self.midi_input_thread.terminate(); self.midi_input_thread.wait()
            try: self.midi_input_thread.message_received.disconnect(self._parse_midi_message)
            except (TypeError, RuntimeError): pass
            self.midi_input_thread.deleteLater()
            self.midi_input_thread = None; self.in_port_name_used = None
            print("AkaiFireController: MIDI Input stopped.")

    def is_connected(self): return self.out_port is not None and not self.out_port.closed

    def is_input_connected(self): return self.midi_input_thread is not None and self.midi_input_thread.isRunning()

    def _send_cc(self, control, value, channel=0):
        if not self.is_connected(): return
        try: self.out_port.send(mido.Message('control_change', channel=channel, control=control, value=value))
        except Exception as e: print(f"AkaiFireController: Error sending CC: {e}")

    def _initialize_device_leds(self):
        if not self.is_connected(): return
        self.clear_all_pads(); time.sleep(0.02)
        for cc_num in self.NON_GRID_BUTTON_CCS: self._send_cc(control=cc_num, value=LED_OFF)
        self._send_cc(control=self.BANK_LED_CC, value=self.BANK_LED_OFF_VALUE)

    def _send_sysex(self, data_bytes):
        if not self.is_connected(): return
        sysex_header = [0xF0, 0x47, 0x7F, 0x43]; sysex_ender = [0xF7]
        try: self.out_port.send(mido.Message.from_bytes(sysex_header + data_bytes + sysex_ender)); time.sleep(0.002) 
        except Exception as e: print(f"AkaiFireController: Error sending SysEx: {e}")

    def set_global_brightness_factor(self, factor: float):
        self.current_brightness_factor = max(0.0, min(float(factor), 1.0)) # Ensure it's a float and clamped
        # print(f"AkaiCtrl TRACE: Brightness factor set to {self.current_brightness_factor}") # Optional

    def set_pad_color(self, col, row, r8, g8, b8):
        if not self.is_connected() or not (0 <= row <= 3 and 0 <= col <= 15): return
        # Apply global brightness factor
        r_adj = int(r8 * self.current_brightness_factor)
        g_adj = int(g8 * self.current_brightness_factor)
        b_adj = int(b8 * self.current_brightness_factor)
        pad_idx = (row * 16) + col
        # Ensure values are clamped after scaling before 7-bit conversion
        r7 = max(0, min(r_adj, 255)) >> 1
        g7 = max(0, min(g_adj, 255)) >> 1
        b7 = max(0, min(b_adj, 255)) >> 1
        self._send_sysex([0x65, 0x00, 0x04, pad_idx, r7, g7, b7])

    def set_multiple_pads_color(self, pad_data_list, bypass_global_brightness: bool = False):
        if not self.is_connected() or not pad_data_list: return
        payload = []
        count = 0
        brightness_to_apply = 1.0 if bypass_global_brightness else self.current_brightness_factor
        # print(f"AkaiCtrl TRACE: set_multiple_pads_color using brightness_to_apply: {brightness_to_apply}, bypass_flag: {bypass_global_brightness}")
        for item in pad_data_list:
            idx, r8, g8, b8 = -1, 0, 0, 0 # Default values
            if len(item) == 4: # Assuming (idx, r, g, b)
                idx, r8, g8, b8 = item
            elif len(item) == 5: # Assuming (row, col, r, g, b)
                ro, co, r_val, g_val, b_val = item
                if 0 <= ro <= 3 and 0 <= co <= 15:
                    idx = (ro * 16) + co
                    r8, g8, b8 = r_val, g_val, b_val
                else:
                    continue # Skip invalid row/col
            else:
                continue # Skip malformed item
            if idx == -1: continue
            # Apply brightness
            r_adj = int(r8 * brightness_to_apply)
            g_adj = int(g8 * brightness_to_apply)
            b_adj = int(b8 * brightness_to_apply)
            # Ensure values are clamped after scaling before 7-bit conversion
            r7 = max(0, min(r_adj, 255)) >> 1
            g7 = max(0, min(g_adj, 255)) >> 1
            b7 = max(0, min(b_adj, 255)) >> 1
            payload.extend([idx, r7, g7, b7])
            count += 1
        if not payload: return
        length = count * 4 # Each pad entry is 4 bytes (idx, r, g, b) in the SysEx payload
        # print(
        #     f"AFC DEBUG Sysex Payload: Count={count}, Length={length}, Payload Sample (first 20 bytes): {payload[:20]}")
        self._send_sysex([0x65, (length >> 7) & 0x7F, length & 0x7F] + payload)

    def clear_all_pads(self):
        if not self.is_connected(): return
        self.set_multiple_pads_color([(r*16+c,0,0,0) for r in range(4) for c in range(16)])   

    def _parse_midi_message(self, msg: mido.Message):
        if msg.type == 'note_on' or msg.type == 'note_off':
            is_down = msg.type == 'note_on'
            # print(f"DEBUG AkaiFireController: Note ON: {hex(msg.note)}") # <<THIS IS THE DEBUG CALL TO SEE WHAT IS BEING INPUTTED
            self.fire_button_event.emit(msg.note, is_down)
            
            if((msg.note >= FIRE_BUTTON_STEP) and (msg.note<=FIRE_BUTTON_REC)):
                self.buttom_row_buttons_event.emit(is_down, msg.note-FIRE_BUTTON_STEP)
                if   msg.note == FIRE_BUTTON_REC: self.rec_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_STOP: self.stop_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_PLAY: self.play_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_PATTERN_SONG: self.metronome_button_event.emit(is_down)

                elif msg.note == FIRE_BUTTON_ALT: self.alt_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_SHIFT: self.shift_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_PERFORM: self.perform_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_DRUM: self.drum_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_NOTE: self.note_button_event.emit(is_down)
                elif msg.note == FIRE_BUTTON_STEP: self.step_button_event.emit(is_down)

            elif msg.note == FIRE_BUTTON_PATTERN_UP: self.pattern_button_event.emit(is_down, 1)
            elif msg.note == FIRE_BUTTON_PATTERN_DOWN: self.pattern_button_event.emit(is_down, -1)
            elif msg.note == FIRE_BUTTON_BROWSER: self.browser_button_event.emit(is_down)
            elif msg.note == FIRE_BUTTON_SELECT: self.select_button_event.emit(is_down)
            elif msg.note == FIRE_BUTTON_GRID_LEFT: self.grid_button_event.emit(is_down, -1)
            elif msg.note == FIRE_BUTTON_GRID_RIGHT: self.grid_button_event.emit(is_down, 1)

            elif msg.note == FIRE_BUTTON_BANK: self.bank_button_event.emit(is_down)

            elif (msg.note >= FIRE_BUTTON_MUTE_FIRST) and (msg.note < FIRE_BUTTON_MUTE_FIRST+4):
                self.mute_button_event.emit(is_down, msg.note-FIRE_BUTTON_MUTE_FIRST)

            elif (msg.note >= FIRE_BUTTON_PAD_FIRST) and (msg.note < FIRE_BUTTON_PAD_FIRST+64):
                padID = msg.note-FIRE_BUTTON_PAD_FIRST
                padX = padID % 16
                padY = math.floor(padID / 16)
                self.pad_button_event.emit(is_down, padX, padY)

        elif msg.type == 'control_change':
            # print(f"DEBUG AkaiFireController: CC: {hex(msg.control)}, Val: {msg.value}")
            if hasattr(self, 'control_change_event'): # Check if signal exists
                v = msg.value
                if v>64: v = v-128
                id = msg.control - FIRE_KNOB_FIRST
                if msg.control==FIRE_KNOB_SELECT: id = 4
                self.control_change_event.emit(id, v)

    def set_bottom_row_led(self, index: int, state: bool, alt_color: bool = False, bright: bool = True):
        id = index + 44
        v = 1 if alt_color else 2
        if bright: v = v+2
        if state==False: v=0
        self._send_cc(id, v)

    def set_mute_led(self, index: int, state: bool, bright: bool = True):
        id = FIRE_BUTTON_MUTE_FIRST+index
        v = 2 if bright else 1 
        if (not state): v=0
        self._send_cc(id, v)
    
    def set_mute_status_led(self, index: int, state: bool, bright: bool = True):
        self.set_mute_led(index+4, state, bright)

    def set_preset_led(self, index: int, state: bool = True):
        v = index if state else 4
        self._send_cc(LED_PRESETS, v)

    def set_pattern_led(self, index: int, state: bool, bright: bool = True):
        id = FIRE_BUTTON_PATTERN_UP if index==1 else FIRE_BUTTON_PATTERN_DOWN 
        v = 2 if bright else 1 
        if (not state): v=0
        self._send_cc(id, v)

    def set_grid_led(self, index: int, state: bool, bright: bool = True):
        id = FIRE_BUTTON_GRID_RIGHT if index==1 else FIRE_BUTTON_GRID_LEFT
        v = 2 if bright else 1 
        if (not state): v=0
        self._send_cc(id, v)
    
    def set_browser_led(self, state: bool, bright: bool = True):
        v = 2 if bright else 1 
        if (not state): v=0
        self._send_cc(FIRE_BUTTON_BROWSER, v)


    def oled_send_full_bitmap(self, packed_bitmap_data_7bit: bytes | bytearray):
        # print(f"AkaiCtrl TRACE: oled_send_full_bitmap. Connected: {self.is_connected()}, Type: {type(packed_bitmap_data_7bit)}, Len: {len(packed_bitmap_data_7bit) if packed_bitmap_data_7bit is not None else 'None'}")
        if not self.is_connected():
            return
        PACKED_LEN = 1176  # Defined in oled_renderer as PACKED_BITMAP_SIZE_BYTES
        # Check if data is valid (bytes or bytearray and correct length)
        if not isinstance(packed_bitmap_data_7bit, (bytes, bytearray)) or \
            len(packed_bitmap_data_7bit) != PACKED_LEN:
            data_len_str = 'N/A'
            actual_type_str = type(packed_bitmap_data_7bit).__name__
            if packed_bitmap_data_7bit is not None:
                try:
                    data_len_str = f"{len(packed_bitmap_data_7bit)}"
                except TypeError:
                    pass  # len() not applicable (e.g. if it was an int by mistake)
            print(
                f"AkaiFireController: OLED: Invalid 7-bit packed data. Expected {PACKED_LEN} B, got {data_len_str}B. Type: {actual_type_str}")
            return
        ctrl_bytes = [0x00, 0x07, 0x00, 0x7F]
        payload_data = list(packed_bitmap_data_7bit)
        full_payload_for_sysex = ctrl_bytes + payload_data
        payload_length = len(full_payload_for_sysex)
        # Length bytes for SysEx message (high byte, low byte, 7-bit each)
        len_h = (payload_length >> 7) & 0x7F
        len_l = payload_length & 0x7F
        sysex_command_and_data = [0x0E, len_h, len_l] + full_payload_for_sysex
        # _send_sysex will wrap this with F0...F7
        self._send_sysex(sysex_command_and_data)

    def _pack_8bit_to_7bit_sysex_data(self, data_8bit: bytearray) -> list[int]:
        # This function is no longer directly used by oled_send_full_bitmap
        # but kept for potential other uses or reference.
        packed_7bit_data = []; num_src = len(data_8bit)
        for i in range(0, num_src, 7):
            chunk = data_8bit[i:i+7]; n_chunk = len(chunk)
            out_grp = [0]*8
            for j in range(n_chunk): out_grp[j] = chunk[j] & 0x7F
            msbs = 0
            for j in range(n_chunk):
                if (chunk[j] & 0x80): msbs |= (1 << j)
            out_grp[7] = msbs
            packed_7bit_data.extend(out_grp)
        # print(f"DEBUG AkaiFireController (Packer): 8b len: {num_src}, 7b len: {len(packed_7bit_data)}")
        return packed_7bit_data
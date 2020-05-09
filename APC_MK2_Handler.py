import rtmidi
import math
import colorsys


class APC_MK2_Handler(object):
	def __init__(self, in_port, out_port):

		self.ColorMap = [["#000000", 0],   ["#1E1E1E", 1],   ["#7F7F7F", 2],   ["#FFFFFF", 3],   ["#FF4C4C", 4],   ["#FF0000", 5],   ["#590000", 6],   ["#190000", 7], 
						 ["#FFBD6C", 8],   ["#FF5400", 9],   ["#591D00", 10],  ["#271B00", 11],  ["#FFFF4C", 12],  ["#FFFF00", 13],  ["#595900", 14],  ["#191900", 15], 
						 ["#88FF4C", 16],  ["#54FF00", 17],  ["#1D5900", 18],  ["#142B00", 19],  ["#4CFF4C", 20],  ["#00FF00", 21],  ["#005900", 22],  ["#001900", 23], 
						 ["#4CFF5E", 24],  ["#00FF19", 25],  ["#00590D", 26],  ["#001902", 27],  ["#4CFF88", 28],  ["#00FF55", 29],  ["#00591D", 30],  ["#001F12", 31], 
						 ["#4CFFB7", 32],  ["#00FF99", 33],  ["#005935", 34],  ["#001912", 35],  ["#4CC3FF", 36],  ["#00A9FF", 37],  ["#004152", 38],  ["#001019", 39], 
						 ["#4C88FF", 40],  ["#0055FF", 41],  ["#001D59", 42],  ["#000819", 43],  ["#4C4CFF", 44],  ["#0000FF", 45],  ["#000059", 46],  ["#000019", 47], 
						 ["#874CFF", 48],  ["#5400FF", 49],  ["#190064", 50],  ["#0F0030", 51],  ["#FF4CFF", 52],  ["#FF00FF", 53],  ["#590059", 54],  ["#190019", 55], 
						 ["#FF4C87", 56],  ["#FF0054", 57],  ["#59001D", 58],  ["#220013", 59],  ["#FF1500", 60],  ["#993500", 61],  ["#795100", 62],  ["#436400", 63], 
						 ["#033900", 64],  ["#005735", 65],  ["#00547F", 66],  ["#0000FF", 67],  ["#00454F", 68],  ["#2500CC", 69],  ["#7F7F7F", 70],  ["#202020", 71], 
						 ["#FF0000", 72],  ["#BDFF2D", 73],  ["#AFED06", 74],  ["#64FF09", 75],  ["#108B00", 76],  ["#00FF87", 77],  ["#00A9FF", 78],  ["#002AFF", 79], 
						 ["#3F00FF", 80],  ["#7A00FF", 81],  ["#B21A7D", 82],  ["#402100", 83],  ["#FF4A00", 84],  ["#88E106", 85],  ["#72FF15", 86],  ["#00FF00", 87], 
						 ["#3BFF26", 88],  ["#59FF71", 89],  ["#38FFCC", 90],  ["#5B8AFF", 91],  ["#3151C6", 92],  ["#877FE9", 93],  ["#D31DFF", 94],  ["#FF005D", 95], 
						 ["#FF7F00", 96],  ["#B9B000", 97],  ["#90FF00", 98],  ["#835D07", 99],  ["#392b00", 100], ["#144C10", 101], ["#0D5038", 102], ["#15152A", 103], 
						 ["#16205A", 104], ["#693C1C", 105], ["#A8000A", 106], ["#DE513D", 107], ["#D86A1C", 108], ["#FFE126", 109], ["#9EE12F", 110], ["#67B50F", 111], 
						 ["#1E1E30", 112], ["#DCFF6B", 113], ["#80FFBD", 114], ["#9A99FF", 115], ["#8E66FF", 116], ["#404040", 117], ["#757575", 118], ["#E0FFFF", 119], 
						 ["#A00000", 120], ["#350000", 121], ["#1AD000", 122], ["#074200", 123], ["#B9B000", 124], ["#3F3100", 125], ["#B35F00", 126], ["#4B1502", 127]]
		
		self.inport  = in_port
		self.outport = out_port

		self.Pages = [PAD_EXEC_PAGE(1), PAD_EXEC_PAGE(2), PAD_EXEC_PAGE(3), PAD_EXEC_PAGE(4), PAD_EXEC_PAGE(5), PAD_EXEC_PAGE(6), PAD_EXEC_PAGE(7), PAD_EXEC_PAGE(8)]

		self.mode_message = [0xF0, 0x47, 0x7F, 0x29, 0x60, 0x00, 0x04, 0x42, 0x08, 0x02, 0x01, 0xF7]

		self.MidiOut = rtmidi.MidiOut()
		self.MidiIn  = rtmidi.MidiIn()
		self.last_data = None

		self.MidiOpen = False
		self.current_page = 0

	def hex_to_rgb(self, hex):
		hex = hex.lstrip('#')
		return tuple(int(hex[i:i+2], 16) for i in range(0, 6, 2))

	def get_color_val(self, hex_color_str):
		target_color = self.hex_to_rgb(hex_color_str)
		target_hsv = colorsys.rgb_to_hsv(target_color[0], target_color[1], target_color[2])
		last_stored = [[None, None], None]
		for color_map_entry in self.ColorMap:
			compare_color = self.hex_to_rgb(color_map_entry[0])
			compare_hsv = colorsys.rgb_to_hsv(compare_color[0], compare_color[1], compare_color[2])
			difference = math.sqrt((target_color[0] - compare_color[0])**2 + (target_color[1] - compare_color[1])**2 + (target_color[2] - compare_color[2])**2)
			hue_difference = abs(target_hsv[0] - compare_hsv[0])
			if last_stored[0][0] == None or last_stored[0][0] > difference and last_stored[0][1] >= hue_difference:
				last_stored = [[difference, hue_difference], color_map_entry[1]]
		return last_stored[1]

	def open_midi(self):
		self.MidiIn.open_port(self.inport)
		self.MidiOut.open_port(self.outport)

		self.MidiOut.send_message(self.mode_message)
		self.MidiOut.send_message([144, 51, 127])
		self.MidiOpen = True

	def close_midi(self):
		if self.MidiOpen:
			self.MidiIn.close_port()
			self.MidiOut.close_port()
			self.MidiOpen = False

	def set_page(self, indx):
		print("Setting Page ", indx)
		ret = False
		if indx != self.current_page:
			ret = True
			new_ch = indx + 144
			old_ch = self.current_page + 128
			self.MidiOut.send_message([new_ch, 51, 127])
			self.MidiOut.send_message([old_ch, 51, 0])
			self.current_page = indx
			self.load_page_info()
		return(ret)

	def set_color(self, key, hex, mode, running):
		vel = self.get_color_val(hex)
		ch = 0

		if self.Pages[self.current_page].type == "EXEC":
			if mode == "PULSE":
				ch = 9
			if mode == "BLINK":
				ch = 8

		self.Pages[self.current_page].set_Color(key, hex, ch, running)
		self.MidiOut.send_message([144+ch, key, vel])

	def load_page_info(self):
		Page = self.Pages[self.current_page]
		Buttons = Page.BUTTONS

		for b in range(len(Buttons)):
			hex_a = Buttons[b][0]
			hex_b = Buttons[b][1]
			mode  = Buttons[b][2]
			cl_val = self.get_color_val(hex_a)
			self.MidiOut.send_message([144, b, cl_val])
			if mode != 0:
				cl_val = self.get_color_val(hex_b)
				self.MidiOut.send_message([144 + mode, b, cl_val])

	def set_button_data(self, data):
		for entry in data:
			exec_id = int(entry[0])
			indx = exec_id - 101 + 32
			if exec_id >= 111: indx = exec_id - 111 + 24
			if exec_id >= 121: indx = exec_id - 121 + 16
			if exec_id >= 131: indx = exec_id - 131 + 8
			if exec_id >= 141: indx = exec_id - 141
			valid = False
			
			
			if 101 <= exec_id <= 108 or 111 <= exec_id <= 118 or 121 <= exec_id <= 128 or 131 <= exec_id <= 138 or 141 <= exec_id <= 148:
				valid = True
				last_data_set = self.Pages[self.current_page].BUTTONS[indx]
				if entry[2] == last_data_set[4] and entry[4] == last_data_set[0]: valid = False
			if entry[1] != "" and valid:
				running = entry[2]
				color = entry[4]
				command = entry[5]
				
				self.Pages[self.current_page].set_command(indx, command)
				self.set_color(indx, color, "NORMAL", running)
				if running == 1:
					if entry[1] == "LT":
						self.set_color(indx, "#000000", "BLINK", running)
					else:
						self.set_color(indx, "#FFFFFF", "PULSE", running)
			else: 
				if valid: self.set_color(indx, '#000000', "NORMAL", 0)

	def set_fader_value(self, data):
		for i in range(8):
			val = data[i] * 127
			key = 48 + i
			self.MidiOut.send_message([176, key, val])

	def get_button(self, key):
		return self.Pages[self.current_page].get_exec(key)

	def set_static_fader_buttons(self, list):
		for i in range(8):
			if list[i][0] != "Empty":
				v = list[i][1]
				self.MidiOut.send_message([144 + i, 49, 127])
				self.MidiOut.send_message([144 + i, 50, v])
				self.MidiOut.send_message([144 + i, 66, v*2])

class PAD_EXEC_PAGE(object):
	def __init__(self, exec_page):
		self.page = exec_page
		self.type = "EXEC"
		self.BUTTONS = []
		for i in range(40):
			exec = 141 + i
			if i >=  8: exec =  131 + i - 8
			if i >= 16: exec = 121 +  i - 16
			if i >= 24: exec = 111 +  i - 24
			if i >= 32: exec = 101 +  i - 32
			self.BUTTONS.append(["#000000", "#000000", 0, "NONE", 0, exec])

	def set_Color(self, indx, value, mode, is_running):
		self.BUTTONS[indx][4] = is_running
		if mode == 0:
			self.BUTTONS[indx][0] = value
			self.BUTTONS[indx][1] = "#000000"
			self.BUTTONS[indx][2] = mode

		if mode != 0:
			self.BUTTONS[indx][1] = value
			self.BUTTONS[indx][2] = mode

	def get_exec(self, indx):
		return self.BUTTONS[indx][5]

	def set_command(self, indx, command):
		self.BUTTONS[indx][3] = command
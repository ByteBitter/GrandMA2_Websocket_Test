
import APC_MK2_Handler
import ma_websocket
import time

def midi_callback(data, b):
	mssg, time = data
	print(mssg)
	if 144 <= mssg[0] <= 151 and mssg[1] == 51 and mssg[2] == 127:
		conf = APC.set_page(mssg[0] - 144)
		if conf: MaSock.send_command("page " + str(mssg[0] - 143))
	
	if mssg[0] == 144 and 0 <= mssg[1] <= 39:
		MaSock.set_button(APC.current_page, APC.get_button(mssg[1]), 1, 0)

	if mssg[0] == 128 and 0 <= mssg[1] <= 39:
		MaSock.set_button(APC.current_page, APC.get_button(mssg[1]), 0, 0)

	if mssg[0] == 176 and 48 <= mssg[1] <= 55:
		MaSock.set_fader(APC.current_page, mssg[1] - 48 + 15, mssg[2])

	if 176 <= mssg[0] <= 183 and mssg[1] == 7:
		MaSock.set_fader(0, mssg[0] - 176, mssg[2])

	if mssg[0] == 176 and mssg[1] == 14:
		MaSock.set_fader(0, 8, mssg[2])

	if 144 <= mssg[0] <= 151:
		if mssg[1] == 49: MaSock.set_button(0, mssg[0] - 143, 1, 0)
		if mssg[1] == 50: MaSock.set_button(0, mssg[0] - 143, 1, 1)
		if mssg[1] == 66: MaSock.set_button(0, mssg[0] - 143, 1, 2)

	if 128 <= mssg[0] <= 135:
		if mssg[1] == 49: MaSock.set_button(0, mssg[0] - 127, 0, 0)
		if mssg[1] == 50: MaSock.set_button(0, mssg[0] - 127, 0, 1)
		if mssg[1] == 66: MaSock.set_button(0, mssg[0] - 127, 0, 2)


APC = APC_MK2_Handler.APC_MK2_Handler(1, 2)
MaSock = ma_websocket.ma_websocket("ws://127.0.0.1/?ma=1", "Niklas", "") 
MaSock.login()
APC.open_midi()
keep_alive_counter = 0

APC.MidiIn.set_callback(midi_callback)

while True:
	time.sleep(0.05)
	keep_alive_counter = keep_alive_counter + 1

	playback_button_data = MaSock.playbacks(APC.current_page)
	if playback_button_data != None: APC.set_button_data(playback_button_data)

	playback_fader_data = MaSock.playback_fader(APC.current_page)
	if playback_fader_data != None: APC.set_fader_value(playback_fader_data)

	static_fader_data = MaSock.get_static_exec_status()
	if static_fader_data != None: APC.set_static_fader_buttons(static_fader_data)

	if keep_alive_counter == 25:
		MaSock.keep_alive()
		keep_alive_counter = 0
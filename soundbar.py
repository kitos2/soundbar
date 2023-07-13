#!/usr/bin/env python
# -*- coding: utf-8 -*-
# kitos 15-8-2021
# soundbar.py
# 
# tool for detecting all sound devices and displaying them on the i3status bar.
# made to work with ttf-symbola

import sys
import json
import subprocess
import os

usb_icon = '🎧'
default_icon = '🔊'
muted_icon = '🔇'



def get_devices():
	devices_read = subprocess.check_output("pactl list sinks", shell=True)

	devices_status = devices_read.decode('utf-8')
	devices_status = devices_status.split("Sink #")[1:]
	return devices_status
	
	
def parse_devices(devices):
	soundbar = []
	
	for d in devices:
		soundbar.append(create_device_status(d))
			
	return soundbar

	
def create_device_status(d):
	icon = ''
	
	name = d.split('\tName: alsa_output.')[1].split('\n',1)[0]
	
	if 'usb' in name:
		icon = usb_icon
	elif 'hdmi' in name:
		return ''
		icon = hdmi_icon
	else:
		icon = default_icon
	
	
	if d.split('Mute: ')[1].split('\n',1)[0].strip() == 'no':
		volume = d.split('\tVolume:')[1].split('/',1)[1].split('/',1)[0].strip()
	else:
		volume = 'muted'
		icon = muted_icon
	
	state = d.split('\tState:')[1].split('\n',1)[0]
	
	if 'RUNNING' in state:
		icon = icon + '*'
	
	return icon + ':' + volume

	
def read_line():
	""" Interrupted respecting reader for stdin. """
	# try reading a line, removing any extra whitespace
	try:
		line = sys.stdin.readline().strip()
		# i3status sends EOF, or an empty line
		if not line:
			sys.exit(3)
		return line
	# exit on ctrl-c
	except KeyboardInterrupt:
		sys.exit()	

	
def print_line(message):
	""" Non-buffered printing to stdout. """
	sys.stdout.write(message + '\n')
	sys.stdout.flush()


if __name__ == '__main__':
	# Skip the first line which contains the version header.
	print_line(read_line())
	# The second line contains the start of the infinite array.
	print_line(read_line())
	
	while True:
		line, prefix = read_line(), ''
		# ignore comma at start of lines
		if line.startswith(','):
			line, prefix = line[1:], ','
			
		j = json.loads(line)
		
		
		# read sound device info 
		devices = get_devices()
		soundbar = parse_devices(devices)
		
		# insert information into the start of the json, but could be anywhere
		# CHANGE THIS LINE TO INSERT SOMETHING ELSE
		for device in reversed(soundbar):
			color = '#ffffff'
			if 'muted' in device:
				color = '#ffff00'
			j.insert(0, {'color' : color, 'full_text' : device, 'name' : 'soundbar'})
		
		# echo back new encoded json
		print_line(prefix+json.dumps(j))
		

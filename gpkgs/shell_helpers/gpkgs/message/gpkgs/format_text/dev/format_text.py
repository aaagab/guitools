#!/usr/bin/env python3
# author: Gabriel Auger
# version: 0.3.0
# name: format_text
# license: MIT
import re
import sys

class Format_text(object):
	@staticmethod
	def color_dyn_function(color_name):
		def function_template(txt):
			return Format_text.color(color_name, txt)
		return function_template

	@staticmethod
	def emphasize_dyn_function(mark_name):
		def function_template(txt):
			return Format_text.mark(mark_name, txt)
		return function_template

	@staticmethod
	def log_dyn_function(log_label):
		def function_template(txt):
			return Format_text.log(log_label, txt)
		return function_template
	
	@staticmethod
	def clear_screen():
		print("\x1b[2J")
		print("\x1b[H")
	
	@staticmethod
	def clear_scrolling_history():
		print("\x1b[2J\x1b[H\x1b[3J", end="")

	@staticmethod
	def color(color_name, text):
		code1, code2 = Format_text.get_colors(color_name)
		return str("\x1b[{};{}m{}\x1b[0m".format(code1,code2,re.sub("(\\x1b\[\d;\dm|\\x1b\[\dm)", "", text)))

	@staticmethod
	def mark(mark_name, text):
		code = Format_text.get_marks(mark_name)
		return str("\x1b[{}m{}\x1b[0m".format(code,re.sub("(\\x1b\[\d;\dm|\\x1b\[\dm)", "", text)))

	@staticmethod
	def get_logs(log_type=None):
		prefix="  "
		log_types={
			"error":{
				"prefix":prefix,
				"symbol":"\u00D7",
				"symbol_color": "lRed",
				"text_color": "red"
			},
			"info":{
				"prefix":prefix,
				"symbol":"#",
				"symbol_color": "cyan",
				"text_color": None
			},
			"success":{
				"prefix":prefix,
				"symbol":"\u221A",
				"symbol_color": "lGreen",
				"text_color": None
			},
			"warning":{
				"prefix":prefix,
				"symbol":"\u2206",
				"symbol_color": "yellow",
				"text_color": None
			}
		}
		if log_type is None:
			return log_types
		else:
			if log_type not in log_types:
				print(Format_text.error("Log type '{}' not found".format(log_type)))
				sys.exit(1)
			return log_types[log_type]

	@staticmethod
	def log(log_type, text):
		if not isinstance(log_type, dict):
			log_type=Format_text.get_logs(log_type)

		if log_type["text_color"] is not None:
			text=Format_text.color(log_type["text_color"], text)

		symbol=None
		if log_type["symbol_color"] is not None:
			symbol=Format_text.color(log_type["symbol_color"], log_type["symbol"])
		else:
			symbol=log_type["symbol"]

		return "{}{} {}".format(log_type["prefix"], symbol, text)
		
	@staticmethod
	def get_colors(color_name=None):
		colors={
			"black":[0,30],
			"blue":[0,34],
			"brown":[0,33],
			"cyan":[0,36],
			"dGray":[1,30],
			"green":[0,32],
			"lBlue":[1,34],
			"lCyan":[1,36],
			"lGray":[0,37],
			"lGreen":[1,32],
			"lMagenta":[1,35],
			"lRed":[1,31],
			"magenta":[0,35],
			"red":[0,31],
			"white":[1,37],
			"yellow":[1,33],
		}
		if color_name is None:
			return colors
		else:
			if color_name not in colors:
				print(Format_text.error("Color Name '{}' not found".format(color_name)))
				sys.exit(1)
			return colors[color_name]

	@staticmethod
	def get_marks(mark_name=None):
		marks={
			"bold": 1,
			"iverse": 7,
			"uline": 4,
		}
		if mark_name is None:
			return marks
		else:
			if mark_name not in marks:
				print(Format_text.error("Mark Name '{}' not found".format(mark_name)))
				sys.exit(1)
			return marks[mark_name]

	# the individual function are created here
	black=color_dyn_function.__func__("black")
	red=color_dyn_function.__func__("red")
	green=color_dyn_function.__func__("green")
	brown=color_dyn_function.__func__("brown")
	blue=color_dyn_function.__func__("blue")
	magenta=color_dyn_function.__func__("magenta")
	cyan=color_dyn_function.__func__("cyan")
	lGray=color_dyn_function.__func__("lGray")
	dGray=color_dyn_function.__func__("dGray")
	lRed=color_dyn_function.__func__("lRed")
	lGreen=color_dyn_function.__func__("lGreen")
	yellow=color_dyn_function.__func__("yellow")
	lBlue=color_dyn_function.__func__("lBlue")
	lMagenta=color_dyn_function.__func__("lMagenta")
	lCyan=color_dyn_function.__func__("lCyan")
	white=color_dyn_function.__func__("white")
	
	bold=emphasize_dyn_function.__func__("bold")
	uline=emphasize_dyn_function.__func__("uline")
	iverse=emphasize_dyn_function.__func__("iverse")

	error=log_dyn_function.__func__("error")
	info=log_dyn_function.__func__("info")
	success=log_dyn_function.__func__("success")
	warning=log_dyn_function.__func__("warning")

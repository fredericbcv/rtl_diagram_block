#!python

import os, sys, json, argparse
from PIL import Image, ImageDraw, ImageFont

def is_comment(port_list):
	if "comment" in port_list.keys():
		if port_list["comment"].lower() == "true":
			return True
	return False

def gen_diagram_block(file_path):

	# Open file
	with open(file_path) as file:
		file_content = file.read()

	# Save file name
	file_basename = os.path.basename(file_path)
	file_name     = os.path.splitext(file_basename)[0]

	# Load json file
	entity_dict = json.loads(file_content)

	# Symbol param
	rectangle_padding = {"top":15, "right":10, "bottom":15, "left":10}
	canvas_padding 	  = {"top":25, "right":25, "bottom":25, "left":25}
	line_padding      = {"top":0,  "right":5,  "bottom":0,  "left":5}
	ipname_size 	  = 20
	ipname_font 	  = ImageFont.truetype("calibrib.ttf",ipname_size,encoding="unic")
	portname_size     = 20
	portname_font 	  = ImageFont.truetype("calibri.ttf",portname_size,encoding="unic")
	porttype_size 	  = 18
	porttype_font 	  = ImageFont.truetype("calibrii.ttf",porttype_size,encoding="unic")
	line_size 		  = 20
	port_width_factor = 1.4

	# Calc canvas size
	canvas_width  	= rectangle_padding["left"] + rectangle_padding["right"]
	canvas_heigth 	= rectangle_padding["top"]  + rectangle_padding["bottom"]

	# Calc ip_name size
	text_x, text_y, text_width, text_height = ipname_font.getbbox(entity_dict["name"])
	canvas_width 	+= text_width
	canvas_heigth	+= ipname_size

	# Make left & right list
	left_port_list  = list()
	right_port_list = list()
	for port in entity_dict["port_list"]:
		if "align" in port.keys():
			if "right" in port["align"]:
				right_port_list.append(port)
			else:
				left_port_list.append(port)
			continue
		else:
			if "direction" in port.keys():
				if "output" in port["direction"]:
					right_port_list.append(port)
					continue
			
			# Others	
			left_port_list.append(port)

	# Save rectangle size
	rectangle_width  = canvas_width
	rectangle_heigth = canvas_heigth

	# Calc port size
	max_left_type  = 0
	max_right_type = 0
	for x in range(max([len(left_port_list),len(right_port_list)])):
		port_width  = 0

		left_value = ""
		if x < len(left_port_list):
			# port name
			left_value = left_port_list[x]["name"]
			if is_comment(left_port_list[x]):
				text_x, text_y, text_width, text_height = portname_font.getbbox(left_value.upper())
			else:
				text_x, text_y, text_width, text_height = portname_font.getbbox(left_value)
			port_width += text_width
			# port type
			left_value = left_port_list[x]["type"]
			text_x, text_y, text_width, text_height = porttype_font.getbbox(left_value)
			type_width = text_width + line_size + line_padding["left"]
			max_left_type = max(max_left_type,type_width)

		right_value = ""
		if x < len(right_port_list):
			# port name
			right_value = right_port_list[x]["name"]
			if is_comment(right_port_list[x]):
				text_x, text_y, text_width, text_height = portname_font.getbbox(right_value.upper())
			else:
				text_x, text_y, text_width, text_height = portname_font.getbbox(right_value)
			port_width += text_width
			# port type
			right_value = right_port_list[x]["type"]
			text_x, text_y, text_width, text_height = porttype_font.getbbox(right_value)
			type_width = text_width + line_size + line_padding["right"]
			max_right_type = max(max_right_type,type_width)

		# Incr width
		if int(port_width*port_width_factor) > rectangle_width:
			rectangle_width = int(port_width*port_width_factor)

		# Incr canvas
		if rectangle_width + max_left_type + max_right_type > canvas_width:
			canvas_width  = rectangle_width + max_left_type + max_right_type

		canvas_heigth += portname_size

	# Save rectangle size
	rectangle_heigth = canvas_heigth

	# Add padding between title & port
	canvas_heigth    += rectangle_padding["top"]
	rectangle_heigth += rectangle_padding["top"]

	# Add Canvas padding
	canvas_width 	+= canvas_padding["left"] + canvas_padding["right"]
	canvas_heigth 	+= canvas_padding["top"]  + canvas_padding["bottom"]

	# Create canvas
	canvas = Image.new('RGBA',(canvas_width, canvas_heigth), "white")
	draw = ImageDraw.Draw(canvas)

	# Draw rectangle
	if max_left_type == 0:
		rectangle_x0 = canvas_padding["left"]
	else:
		rectangle_x0 = canvas_padding["left"] + max_left_type
	rectangle_y0 = canvas_padding["top"]
	if max_left_type == 0:
		rectangle_x1 = canvas_padding["left"] + rectangle_width
	else:
		rectangle_x1 = canvas_padding["left"] + max_left_type + rectangle_width
	rectangle_y1 = rectangle_heigth+canvas_padding["top"]
	draw.rectangle(((rectangle_x0,rectangle_y0), (rectangle_x1,rectangle_y1)), fill=None, outline="black", width=3)

	# Add ip_name
	text_x, text_y, text_width, text_height = ipname_font.getbbox(entity_dict["name"])
	title_x = rectangle_x0 + (rectangle_width - text_width)/2
	title_y = canvas_padding["top"] + rectangle_padding["top"]
	draw.text((title_x,title_y), entity_dict["name"], 'black', ipname_font)

	text_x_offset = rectangle_x0 + rectangle_padding["left"]
	text_y_offset = canvas_padding["top"]  + rectangle_padding["top"] + ipname_size + rectangle_padding["top"]

	for x in range(max([len(left_port_list),len(right_port_list)])):
		left_value = ""
		if x < len(left_port_list):
			left_value = left_port_list[x]["name"]
			text_x, text_y, text_width, text_height = portname_font.getbbox(left_value)
			comment = is_comment(left_port_list[x])

			# Draw name port
			text_x = text_x_offset
			text_y = text_y_offset + x*portname_size
			if comment:
				draw.text( (text_x,text_y), left_value.upper(), 'gray', portname_font )
			else:
				draw.text( (text_x,text_y), left_value, 'black', portname_font )

			if not comment:
				# Draw type port
				left_value = left_port_list[x]["type"]
				text_x, text_y, text_width, text_height = porttype_font.getbbox(left_value)
				text_x = rectangle_x0 - line_size - text_width - line_padding["left"]
				text_y = text_y_offset + x*portname_size
				draw.text( (text_x,text_y), left_value, 'gray', porttype_font )

				# Draw signal/bus line
				line_x0 = rectangle_x0
				line_y0 = text_y_offset + x*portname_size + portname_size/2
				line_x1 = rectangle_x0 - line_size
				line_y1 = line_y0
				if left_port_list[x]["type"].lower() in ["wire","bit","logic"]:
					line_width = 1
				else:
					line_width = 3
				draw.line( ((line_x0,line_y0), (line_x1,line_y1)), fill="black", width=line_width )

				# Draw direction
				if left_port_list[x]["direction"].lower() == "input":
					draw.line( ((line_x0,line_y0), (line_x0-7,line_y0-7)), fill="black", width=line_width )
					draw.line( ((line_x0,line_y0), (line_x0-7,line_y0+7)), fill="black", width=line_width )
				if left_port_list[x]["direction"].lower() == "output":
					draw.line( ((line_x1,line_y1), (line_x1+7,line_y1-7)), fill="black", width=line_width )
					draw.line( ((line_x1,line_y1), (line_x1+7,line_y1+7)), fill="black", width=line_width )
				if left_port_list[x]["direction"].lower() == "inout":
					draw.line( ((line_x0,line_y0), (line_x0-7,line_y0-7)), fill="black", width=line_width )
					draw.line( ((line_x0,line_y0), (line_x0-7,line_y0+7)), fill="black", width=line_width )
					draw.line( ((line_x1,line_y1), (line_x1+7,line_y1-7)), fill="black", width=line_width )
					draw.line( ((line_x1,line_y1), (line_x1+7,line_y1+7)), fill="black", width=line_width )


		right_value = ""
		if x < len(right_port_list):
			right_value = right_port_list[x]["name"]
			comment = is_comment(right_port_list[x])

			if comment:
				text_x, text_y, text_width, text_height = portname_font.getbbox(right_value.upper())
			else:
				text_x, text_y, text_width, text_height = portname_font.getbbox(right_value)

			# Draw name port
			text_x = rectangle_x1 - rectangle_padding["right"] - text_width
			text_y = text_y_offset + x*portname_size
			if comment:
				draw.text( (text_x,text_y), right_value.upper(), 'gray', portname_font )
			else:
				draw.text( (text_x,text_y), right_value, 'black', portname_font )

			if not comment:
				# Draw type port
				right_value = right_port_list[x]["type"]
				text_x, text_y, text_width, text_height = porttype_font.getbbox(right_value)
				text_x = rectangle_x1 + line_size + line_padding["right"]
				text_y = text_y_offset + x*portname_size
				draw.text( (text_x,text_y), right_value, 'gray', porttype_font )

				# Draw signal/bus line
				line_x0 = rectangle_x1
				line_y0 = text_y_offset + x*portname_size + portname_size/2
				line_x1 = rectangle_x1 + line_size
				line_y1 = line_y0
				if right_port_list[x]["type"].lower() in ["wire","bit","logic"]:
					line_width = 1
				else:
					line_width = 3
				draw.line( ((line_x0,line_y0), (line_x1,line_y1)), fill="black", width=line_width )

				# Draw direction
				if right_port_list[x]["direction"].lower() == "input":
					draw.line( ((line_x0,line_y0), (line_x0+7,line_y0-7)), fill="black", width=line_width )
					draw.line( ((line_x0,line_y0), (line_x0+7,line_y0+7)), fill="black", width=line_width )
				if right_port_list[x]["direction"].lower() == "output":
					draw.line( ((line_x1,line_y1), (line_x1-7,line_y1-7)), fill="black", width=line_width )
					draw.line( ((line_x1,line_y1), (line_x1-7,line_y1+7)), fill="black", width=line_width )
				if right_port_list[x]["direction"].lower() == "inout":
					draw.line( ((line_x0,line_y0), (line_x0+7,line_y0-7)), fill="black", width=line_width )
					draw.line( ((line_x0,line_y0), (line_x0+7,line_y0+7)), fill="black", width=line_width )
					draw.line( ((line_x1,line_y1), (line_x1-7,line_y1-7)), fill="black", width=line_width )
					draw.line( ((line_x1,line_y1), (line_x1-7,line_y1+7)), fill="black", width=line_width )

	canvas.save(file_name+".png", "PNG")
	canvas.show()

def get_args():
    parser = argparse.ArgumentParser(
        description="Generate diagram block"
    )
    parser.add_argument('file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    gen_diagram_block(args.file)

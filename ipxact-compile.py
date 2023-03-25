#!/usr/bin/env python3

print("""
# ipxact-compile reads an ipxact formated xml file and outputs a
# compilation script for a selected tool
# please comment/suggest/request/contribute changes at:
# https://github.com/ThomasGeroudet/ipxact-compile
#
# Copyright (C) 2023 Thomas GEROUDET
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
""")

import argparse
import os
import sys
import xml.etree.ElementTree as ET


if not (sys.version_info.major >= 3 and sys.version_info.minor >= 8):
	print("error: python minimum version 3.8 required for xml.etree.ElementTree findall() support for {*} but found python version " + ".".join(map(str, sys.version_info[:2])))
	sys.exit(1)


parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', help="path of xml file to read", required=True)
parser.add_argument('--output', '-o', help="path of compile script to write", required=True)
parser.add_argument('--tool', '-t', help="generate compile script for this tool", required=True)
parser.add_argument('--compile-options', '-co', default="", help="options to add to the tool compile command")
arguments = parser.parse_args()


tree = ET.parse(arguments.input)
root = tree.getroot()


name = 'name'
#print('information: find ' + name)
nodes = tree.findall('{*}' + name)
if len(nodes) == 0:
	print('error: xml contains no top <' + name + '></' + name + '> element')
elif len(nodes) > 1:
	print('error: xml contains multiple top <' + name + '></' + name + '> elements')
else:
	top_name = nodes[0].text
	#print('information: top name = ' + top_name)


name = 'fileSets'
#print('information: find ' + name)
nodes = tree.findall('{*}' + name)
if len(nodes) == 0:
	print('error: xml contains no top <' + name + '></' + name + '> element')
elif len(nodes) > 1:
	print('error: xml contains multiple top <' + name + '></' + name + '> elements')
else:
	node_filesets = nodes[0]
	#print('information: found one top ' + name)


name = 'fileSet'
#print('information: find ' + name)
nodes = node_filesets.findall('./{*}' + name)
if len(nodes) == 0:
	print('error: xml contains no <' + name + '></' + name + '> element')
elif len(nodes) > 1:
	print('warning: xml contains multiple <' + name + '></' + name + '> elements, will use the first one')
	node_fileset = nodes[0]
else:
	node_fileset = nodes[0]
	#print('information: found one ' + name)


name = 'name'
#print('information: find ' + name)
nodes = node_fileset.findall('./{*}' + name)
if len(nodes) == 0:
	print('error: xml contains no <' + name + '></' + name + '> element')
elif len(nodes) > 1:
	print('error: xml contains multiple <' + name + '></' + name + '> elements')
else:
	fileset_name = nodes[0].text
	#print('information: fileset name = ' + fileset_name)


files = []
name = 'file'
#print('information: find ' + name)
file_nodes = node_fileset.findall('./{*}' + name)
if len(nodes) == 0:
	print('error: xml contains no <' + name + '></' + name + '> element')
else:
	for file_node in file_nodes:
		name = 'name'
		nodes = file_node.findall('./{*}' + name)
		if len(nodes) == 0:
			print('error: file contains no <' + name + '></' + name + '> element')
		elif len(nodes) > 1:
			print('error: file contains multiple <' + name + '></' + name + '> elements')
		else:
			file_name = nodes[0].text
			#print('information: file name = ' + file_name)

		name = 'fileType'
		nodes = file_node.findall('./{*}' + name)
		if len(nodes) == 0:
			print('error: file contains no <' + name + '></' + name + '> element')
		elif len(nodes) > 1:
			print('error: file contains multiple <' + name + '></' + name + '> elements')
		else:
			file_type = nodes[0].text
			#print('information: file type = ' + file_type)

		name = 'logicalName'
		nodes = file_node.findall('./{*}' + name)
		if len(nodes) == 0:
			#print('information: file contains no <' + name + '></' + name + '> element')
			file_logical = None
		elif len(nodes) > 1:
			print('error: file contains multiple <' + name + '></' + name + '> elements')
		else:
			file_logical = nodes[0].text
			#print('information: file logical name = ' + file_logical)

		files.append([file_name, file_type, file_logical])

#print(files)


def tool_example(files):
	compile_command = []
	libraries = sorted(set([x[2] for x in files if x[2] != None]))
	for library in libraries:
		compile_command.append("create_library " + library)

	for file in files:
		# fileType lists from http://www.accellera.org/XMLSchema/IPXACT/1685-2014/fileType.xsd
		if file[1] in ["vhdlAmsSource", "vhdlSource", "vhdlSource-87", "vhdlSource-93"]:
			if file[2] == None:
				compile_command.append("compile_vhdl " + file[0])
			else:
				compile_command.append("compile_vhdl -lib " + file[2] + " " + file[0])
		if file[1] in ["verilogAmsSource", "verilogSource", "verilogSource-95", "verilogSource-2001", "systemVerilogSource", "systemVerilogSource-3.0", "systemVerilogSource-3.1", "systemVerilogSource-3.1a"]:
			if file[2] == None:
				compile_command.append("compile_verilog " + file[0])
			else:
				compile_command.append("compile_verilog -lib " + file[2] + " " + file[0])

	compile_command.append("elaborate " + top_name)
	return compile_command


def tool_verilator(files, compile_options):
	print("information: output compile script for verilator")
	compile_command = "verilator " + compile_options
	for file in files:
		# fileType lists from http://www.accellera.org/XMLSchema/IPXACT/1685-2014/fileType.xsd
		if file[1] in ["verilogSource", "verilogSource-95", "verilogSource-2001", "systemVerilogSource", "systemVerilogSource-3.0", "systemVerilogSource-3.1", "systemVerilogSource-3.1a"]:
			compile_command = compile_command + " " + file[0]
		else:
			# todo: is "verilogAmsSource" supported ?
			# todo: change message for unsupported types (vhdl)
			print("warning: ipxact-compile does not know if verilator supports file type: " + file[1] + " for file: " + file[0])
	return [compile_command]


def group_files(files):
	# group consecutive files that have same parameters
	grouped_files = []
	file_list = []
	for i in range(len(files)):
		file_list.append(files[i][0])
		if i == (len(files) - 1) or files[i][1:] != files[i + 1][1:]:
			grouped_files.append([file_list] + files[i][1:])
			file_list = []
	return grouped_files

#tool_example(files)
#tool_verilator(files)

#print(group_files(files))


ouput = None
if arguments.tool == "example":
	output = tool_example(files)
elif arguments.tool == "verilator":
	output = tool_verilator(files, arguments.compile_options)
else:
	print("error: unknown tool: " + arguments.tool)

if output != None:
	with open(arguments.output, "w") as file_output:
		file_output.write("\n".join(output) + "\n")

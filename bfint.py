#!/usr/bin/env python

import sys, socket

# 10 spaces per tab, yes i know that's odd but i've been coding too much asm lately

f = open(sys.argv[1],'r')
program = f.read()

ptr = 0
memptr = 0
mem = [0]*30000
bktstack = []
namedcells = {}

type_direct = 0
type_param = 1
type_pointer = 2
type_relpointer = 3
type_name = 4

linen = 1

s = ""

def checkint(i):
	try:
		a = int(i)
	except:
		return 0;
	return 1;

def error(s):
	print s + " on line %i" % linen
	sys.exit()

while ptr < len(program):
	instruction = program[ptr]
	intype = type_direct
	param = 0
	#print "ptr start %i" % ptr
	if (ptr+1) < len(program):
		if program[ptr+1] == '(':
			ptr += 2
			i = ptr
			startbkt = ptr
			while (program[i] != ')'): i+=1
			bktcont = program[startbkt:i]
			ptr = i
			#print "ptr %i" % ptr
			if (bktcont[0] == '*'):
				intype = type_pointer
				param = int(bktcont[1:])
			elif (bktcont[0] == '&'):
				intype = type_pointer
				param = int(bktcont[1:]) + memptr
			elif (checkint(bktcont)):
				intype = type_param
				param = int(bktcont)
			else:
				intype = type_name
				param = bktcont
	
	if instruction == '<':
		if (intype == type_direct):
			memptr -= 1
		elif (intype == type_param):
			memptr -= param
		elif (intype == type_pointer):
			memptr -= mem[param]
		elif (intype == type_name):
			memptr -= namedcells[param]
	elif instruction == '>':
		if (intype == type_direct):
			memptr += 1
		elif (intype == type_param):
			memptr += param
		elif (intype == type_pointer):
			memptr += mem[param]
		elif (intype == type_name):
			memptr += namedcells[param]
	elif instruction == '^':
		if (intype == type_direct):
			memptr = mem[memptr]
		elif (intype == type_param):
			memptr = param
		elif (intype == type_pointer):
			memptr = mem[param]
		elif (intype == type_name):
			memptr = namedcells[param]
	elif instruction == 'v':
		if (intype == type_direct):
			error("not a valid operation")
		elif (intype == type_param):
			error("not a valid operation")
		elif (intype == type_pointer):
			mem[param] = memptr
		elif (intype == type_name):
			namedcells[param] = memptr
	elif instruction == '+':
		if (intype == type_direct):
			mem[memptr] += 1
		elif (intype == type_param):
			mem[memptr] += param
		elif (intype == type_pointer):
			mem[memptr] += mem[param]
		elif (intype == type_name):
			mem[memptr] += mem[namedcells[param]]
	elif instruction == '-':
		if (intype == type_direct):
			mem[memptr] -= 1
		elif (intype == type_param):
			mem[memptr] -= param
		elif (intype == type_pointer):
			mem[memptr] -= mem[param]
		elif (intype == type_name):
			mem[memptr] -= mem[namedcells[param]]
	elif instruction == '.':
		if (intype == type_direct):
			a = int(mem[memptr])
			sys.stdout.write(chr(a))
			sys.stdout.flush()
		elif (intype == type_param):
			error("writing to file handles not supported yet")
		elif (intype == type_pointer):
			a = int(mem[memptr])
			s.send(chr(a))
		elif (intype == type_name):
			error("not a valid operation")
	elif instruction == '!':
		if (intype == type_direct):
			a = int(mem[memptr])
			sys.stdout.write(str(a) + " ")
			sys.stdout.flush()
		elif (intype == type_param):
			error("writing to file handles not supported yet")
		elif (intype == type_pointer):
			error("not a valid operation")
		elif (intype == type_name):
			error("not a valid operation")
	elif instruction == ',':
		if (intype == type_direct):
			mem[memptr] = sys.stdin.read(1)
		elif (intype == type_param):
			error("reading from to file handles not supported yet")
		elif (intype == type_pointer):
			a = s.recv(1)
			if (len(a)):
				mem[memptr] = ord(a)
			else:
				mem[memptr] = 0127
		elif (intype == type_name):
			error("not a valid operation")		
	#########################################################
	elif instruction == 'c':
		if (intype == type_direct):
			mem[memptr] = 0
		elif (intype == type_param):
			mem[memptr] = param
		elif (intype == type_pointer):
			mem[param] = 0
		elif (intype == type_name):
			for char in param:
				mem[memptr] = ord(char)
				memptr += 1
			mem[memptr] = 0
			memptr += 1
	#########################################################
	elif instruction == "'":
		if (intype == type_direct):
			error("not a valid instruction")
		elif (intype == type_param):
			error("file handle open not implemented yet")
		elif (intype == type_pointer):
			error("not a valid instruction")
		elif (intype == type_name):
			error("file handle open not implemented")
	elif instruction == '"':
		if (intype == type_direct):
			error("not a valid instruction")
		elif (intype == type_param):
			error("tcp/ip handle open not implemented yet")
		elif (intype == type_pointer):
			hostname = ""
			while (mem[param] != 0):
				hostname += chr(mem[param])
				param += 1
			#print hostname
			s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			hostname = hostname.split(":")
			s.connect((hostname[0],int(hostname[1])))
		elif (intype == type_name):
			error("tcp/ip handle open not implemented")	
	elif instruction == '[':
		closeptr = ptr
		bktdepth = 1
		while bktdepth:
			closeptr += 1
			a = program[closeptr]
			if a == '[': bktdepth += 1
			elif a == ']': bktdepth -= 1
		if (program[closeptr+1] == '('):
			if (program[closeptr+2] == "*"):
				i = closeptr+2
				while (program[i] != ")"):
					i+=1
				check = int(program[closeptr+3:i])
				if (mem[check] > 0):
					bktstack.extend([ptr])
				else:
					ptr = i
		else:
			if (mem[memptr] > 0):
				bktstack.extend([ptr])
			else:
				ptr = closeptr-1 # actually this steps onto the ] but then the instruction decoder skips params
	elif instruction == ']':
		if (intype == type_direct):
			if mem[memptr] > 0:
				ptr = bktstack.pop() - 1
		elif (intype == type_pointer):
			if mem[param] > 0:
				ptr = bktstack.pop() - 1
		elif (intype == type_name):
			error("triggers a bug, don't do this yet")
			#if mem[namedcells[param]] > 0:
			#	ptr = bktstack.pop() - 1
		elif (intype == type_param):
			error("not a valid instruction")
		
	#########################################################
	elif instruction == '@':
		if (intype == type_direct):
			sys.exit(mem[memptr])
		elif (intype == type_param):
			error("not a valid instruction")
		elif (intype == type_pointer):
			error("not a valid instruction")
		elif (intype == type_name):
			error("not a valid instruction")
	#########################################################
	elif instruction == ' ':
		sys.stdout.write(' ')
	#########################################################
	elif instruction == '\n':
		linen += 1
	#########################################################
	else:
		print "unknown instruction %s on line %i, ptr %i" % (instruction, linen, ptr)
	ptr += 1

print ""
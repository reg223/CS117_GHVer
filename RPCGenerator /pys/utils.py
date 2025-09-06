#!/bin/env python3

# Utils.py
# The collection of helper functions for filling out proxy and stub templates. 
# makes extensive use of recursion to resolve composite datatypes. 
# 
# Note: arrays of more than 18 dimensions will not work. However, the current 
# framework can be easily adopted by changing each instance of "i" in 
# array-related recursion to "A" to increase the volume to 52.

#BY: Sam Hu and David Chen
import subprocess
import json
import sys
import os
import re


import constants




# ======================================================
# 
# LOAD TEMPLATE
# 
# Trivial helper function that fetches the template from
# given filename and directory, returning a formattable 
# string.
# 
# ======================================================
def load_template(fname) -> str:
  with open(fname,) as f:
      return f.read()

# ======================================================
# 
# GEN FUNC HEADER
# 
# generates the function header
# 
# ======================================================
def gen_funcHeader(funcName, funcInfo) -> str:
  # use void instead if generating stub function headers
  returnType = funcInfo["return_type"] if funcName[:2] != "__" else "void"
  cpp_params = []
  for argument in funcInfo["arguments"]:
    atype = argument["type"]
    aname = argument["name"]
    
    if atype[:2] == "__":
      rtn = atype[2:]
      rtn = re.sub(r"\[", fr" {aname}[",rtn, count=1)
      cpp_params.append(rtn)
    else:
      cpp_params.append(f"{atype} {aname}")
  
  formatted_cpp_params = "(" + ", ".join(cpp_params) + ")"

  return returnType + " " + funcName + " " + formatted_cpp_params


# ======================================================
# 
#  GET SIZE SERIES
#
#  Calculate Size of the list of objects given,
#  Mutually recursive on each other for composite types
#  gen_getSize marks the start of the recursion. One 
#  noteworthy feature it the use of the iterating 
#  character idx. It is ensured that after each usage, 
#  a new usable char is passed on to the next relevant 
#  call, thereby ensuring all nested for-loops from 
#  arrays have unique iterators; This is robust for up 
#  to 18 dimensions (# of alpha char starting from i), 
#  which is considered to be more than enough.
# 
# =======================================================

def gen_getSize(params, typeDict, name = None) -> str:
  res = ""
  for param in params:
       # When name is not None, adapts for stub version
    ptype = param['type'] if name == None else param
    pname = param['name'] if name == None else name
    if ptype in constants.ATOMIC_TYPES:
      res += gen_getSizeAtomic(ptype)
    elif ptype == "string":
      res += gen_getSizeString(pname)
    elif ptype[:2] == "__":
      res += gen_getSizeArray(pname, ptype,typeDict,"i")
    elif typeDict[ptype]: #struct
      res += gen_getSizeStruct(pname, ptype,typeDict,"i")
    else:
      raise ValueError(f"Unknown type \'{ptype}\'")
        
  return res

def gen_getSizeAtomic(ptype) -> str:  
  if ptype != "void":
    return "sendsize += 4;\n"
  else:
    raise TypeError("Void cannot be the type of a parameter")
  
def gen_getSizeString(name) -> str:
  return f"sendsize += {name}.length() + 5;\n"
# *******************************************************
# For each nested layer of members, names are joined with '.'
# *******************************************************
def gen_getSizeStruct(name, type, typeDict,idx) -> str:
  members = typeDict[type]["members"]
  res = ""
  for member in members:
    ptype = member["type"]
    pname = member["name"]
    if ptype in constants.ATOMIC_TYPES:
      res += gen_getSizeAtomic(ptype) 
      # does not require name for size calculation
    elif ptype == "string":
      res += gen_getSizeString('.'.join([name,pname]))
    elif ptype[:2] == "__":
      res += gen_getSizeArray('.'.join([name,pname]),ptype,typeDict,idx)
      idx = chr(ord(idx) + 1)
    elif typeDict[ptype]:
      res += gen_getSizeStruct('.'.join([name,pname]), ptype, typeDict, idx)
      
  return res

def gen_getSizeArray(name, type, typeDict, idx) -> str:
  membertype = typeDict[type]["member_type"]
  num = typeDict[type]["element_count"]
  if membertype in constants.ATOMIC_TYPES:
    return f"sendsize += 4*{str(num)};\n"
  elif membertype == "string":
    repetition = gen_getSizeString(name+f"[{idx}]")
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  elif membertype[:2] == "__":
    repetition = gen_getSizeArray(name+f"[{idx}]", membertype, typeDict, chr(ord(idx) + 1)) # increment the char so that it provides a usable index
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  elif typeDict[membertype]: # struct
    repetition = gen_getSizeStruct(name+f"[{idx}]",membertype,typeDict, chr(ord(idx) + 1)) # increment the char so that it provides a usable index
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  else:
    raise ValueError(f"Unknown type \'{membertype}\'")
  
# ======================================================
# 
#  SEND HEADER
#
#  Composes the string for proxy function's header sent 
#  to stub using the name of the function, which is used 
#  as the unique idntifier of functions across client 
#  and server.
# 
# =======================================================

def gen_sendHeader(funcName) -> str:
  res = f"""
memcpy(sendBuff+offset,\"{funcName}\\0\",sizeof("{funcName}"));
offset += sizeof("{funcName}");

"""+writeSendInt("sendsize")
  return res

# ======================================================
# 
#  WRITE SEND SERIES
#
#  Dedicated for writing data of various types into the 
#  send buffer. Like the getSize Family, recurses on 
#  itself to solve composite data types. Also have a 
#  generic starter function (gen_writeSend) and a similar
#  iterator char.
# 
# =======================================================


def gen_writeSend(params, typeDict, name = None) -> str:
  res = ""
  for param in params:
    #   When name is not None, adapts for stub version
      ptype = param['type'] if name == None else param
      pname = param['name'] if name == None else name
      if ptype in constants.ATOMIC_TYPES:
        res += gen_writeSendAtomic(pname, ptype)
      elif ptype == "string":
        res += gen_writeSendString(pname)
      elif ptype[:2] == "__":
        res += gen_writeSendArray(pname, ptype,typeDict,"i")
      elif typeDict[ptype]:
        res += gen_writeSendStruct(pname, ptype,typeDict,"i")
      else:
        raise ValueError(f"Unknown type \'{ptype}\'")


  return res


def gen_writeSendAtomic(name, ptype) -> str:
  if ptype == "int":
    return writeSendInt(name)
  elif ptype == "float":
    return writeSendFloat(name)
  else:
    raise TypeError("Void cannot be the type of a parameter")
  
  
# *******************************************************
# For int and floats, endianness is controlled by 
# converting with htonl() whenever sending through 
# network, and converted back by ntohl() upon read. These 
# two functions illustrate the write end implementation.
# *******************************************************
def writeSendInt(name)->str:
  return f"intbuff = htonl({name});\nmemcpy(sendBuff+offset, &intbuff, 4);\noffset += 4;\n"

def writeSendFloat(name)->str:
  return f"memcpy(&intbuff,&{name},4);\nintbuff = htonl(intbuff);\nmemcpy(&{name}, &intbuff,4);\nmemcpy(sendBuff+offset, &{name}, 4);\noffset += 4;\n"


# *******************************************************
# For String, a size in int is sent so that we can 
# rely upon that instead of null terminators for reading 
# it. This grants support for binary strings, which may 
# contain null characters.
# *******************************************************
def gen_writeSendString(name) -> str:
  res = writeSendInt(name+".length()+1") + f"memcpy(sendBuff+offset, {name}.c_str(),{name}.length()+1);\noffset += {name}.length()+1;\n"
  return res


def gen_writeSendStruct(name, type, typeDict, idx) -> str:
  members = typeDict[type]["members"]
  res = ""
  for member in members:
    ptype = member["type"]
    pname = member["name"]
    if ptype in constants.ATOMIC_TYPES:
      res += gen_writeSendAtomic('.'.join([name,pname]), ptype)
    elif ptype == "string":
      res += gen_writeSendString('.'.join([name,pname]))
    elif ptype[:2] == "__":
      res += gen_writeSendArray('.'.join([name,pname]), ptype,typeDict,idx)
      idx = chr(ord(idx) + 1)
    elif typeDict[ptype]:
      res += gen_writeSendStruct('.'.join([name,pname]), ptype, typeDict, idx)
      
  return res
# *******************************************************
# For each nested layer of array, "[]" is appended
# *******************************************************
def gen_writeSendArray(name, type, typeDict, idx) -> str:
  membertype = typeDict[type]["member_type"]
  num = typeDict[type]["element_count"]
  
  if membertype in constants.ATOMIC_TYPES:
    repetition = writeSendInt(f"{name}[{idx}]")
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  elif membertype == "string":
    repetition = gen_writeSendString(name+f"[{idx}]")
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  elif membertype[:2] == "__":
    repetition = gen_writeSendArray(name+f"[{idx}]", membertype, typeDict, chr(ord(idx) + 1)) # increment the char so that it provides a usable index
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  elif typeDict[membertype]: # non-built-in type that exists in the 
                             # dict must be a struct 
    repetition = gen_writeSendStruct(name+f"[{idx}]", membertype, typeDict, chr(ord(idx) + 1)) # increment the char so that it provides a usable index
    return constants.FOR_TEMP.format(idx=idx,number=num, repetition=repetition)
  else:
    raise ValueError(f"Unknown type \'{membertype}\'")


# ======================================================
# 
#  FILL INSTANCE
#
#  Upon loading the read message from the socket into a 
#  buffer, fill instance is called for each object to be 
#  instantiated. Like other functions dealing with 
#  multiple datatypes, this functions utilizes recursion 
#  to handle composite data types.
# 
# =======================================================

def fillInstance(returnType, typeDict, name, idx) -> str:
  
  if returnType == "int" :
    return f"memcpy(&intbuff, readBuffer + fetchoffset, 4);\n{name} = ntohl(intbuff);\nfetchoffset += 4;\n" 
  
  elif returnType == "float":
    return f"memcpy(&intbuff, readBuffer + fetchoffset, 4);\nintbuff = ntohl(intbuff);\nmemcpy(&{name},&intbuff, 4);\nfetchoffset += 4;\n" 
  
  elif returnType == "string":
    return f"memcpy(&intbuff, readBuffer + fetchoffset, 4);\nstrleng = ntohl(intbuff);\nfetchoffset += 4;\n{name}.resize(strleng);\nmemcpy(&{name}[0], (readBuffer + fetchoffset), strleng);\nfetchoffset += strleng;\n"
  
  elif returnType == "stringvoid": #for void functions
    return f"memcpy(&{name}[0], (readBuffer + fetchoffset), strleng);\nfetchoffset += strleng;\n"
  
  elif returnType[:2] == "__":
    membertype = typeDict[returnType]["member_type"]
    num = typeDict[returnType]["element_count"]
    repetition = fillInstance(membertype, typeDict, name + f"[{idx}]", chr(ord(idx) + 1))
    return constants.FOR_TEMP.format(idx = idx, number = num, repetition=repetition)
  
  elif typeDict[returnType]:
    res = ""
    members = typeDict[returnType]["members"]
    for m in members:
      res += fillInstance(m["type"],typeDict,'.'.join([name,m["name"]]),idx)
    return res
  else:
    raise TypeError(f"Unkown Type:\'{returnType}\'")
  

# ======================================================
# 
#  PARAMETER DECLARATION
#
#  Given a list of argument dicts for a function, declare
#  each item so that they are available for instantiation
#  later.
# 
# =======================================================
def paramDec(arguments)->str:
  paramDeclaration = ""
  for arg in arguments:
    argType = arg["type"]
    argName = arg["name"]
    if argType[:2] != "__":
      paramDeclaration += f"""{argType} {argName};\n"""
    else:
      rtn = re.sub(r"\[", fr" {argName}[",argType[2:], count=1)
      paramDeclaration += f"{rtn};\n"
  return paramDeclaration


# ======================================================
# 
#  FILL PARAMETER
#
#  Using fillInstance(), fill each instance of the 
#  parameter. Makes the assumption that they have already
#  been declared (most likely by paramDec()).
# 
# =======================================================
def fillParam(arguments, typeDict)->str:
  fillParams = ""
  for arg in arguments:
    fillParams += fillInstance(arg["type"],typeDict,arg["name"],"i")
  return fillParams


# ======================================================
# 
#  GET TRIVIAL DECLARATION
#
#  Used to get pass compiler warnings for the trivial 
#  case of when there is a else case that will not be 
#  triggered in the template, which triggers the "used 
#  uninitialized" error for base types.
# 
# =======================================================

def getTrivialDec(arguments)->str:
  rtn = ""
  for arg in arguments:
    argType = arg["type"]
    argName = arg["name"]
    if argType == "int":
      rtn += f"{argName} = 0;\n"
    elif argType == "float":
      rtn += f"{argName} = 0.0;\n"
    elif argType == "string":
      rtn += f"{argName} = \"\";\n"
  return rtn

# ======================================================
# 
#  CALL FUNCTION
#
#  Writes the code for calling real functions from stub
# 
# =======================================================
def callFunc(funcName, funcInfo)->str:
  return f"""{funcInfo["return_type"]} res = {funcName}({", ".join([arg["name"] for arg in funcInfo["arguments"]])});\n"""


def get_types_and_functions(): 
      #
      #     Make sure invoked properly
      #
  assert len(sys.argv) == 2, "Wrong number of arguments"

  #
  #     Make sure IDL file exists and is readable
  #
  filename = sys.argv[1]
  assert os.path.isfile(filename), f"Path {filename} does not designate a file"
  assert os.access(filename, os.R_OK), f"File {filename} is not readable" 

  #
  #     Make sure idl_to_json exists and is executable
  #
  assert os.path.isfile(constants.IDL_TO_JSON_EXECUTABLE), f"Path {constants.IDL_TO_JSON_EXECUTABLE} does not designate a file...run \"make\" to create it" 
  assert os.access(constants.IDL_TO_JSON_EXECUTABLE, os.X_OK), f"File {constants.IDL_TO_JSON_EXECUTABLE} exists but is not executable"

  #
  #     Parse declarations into a Python dictionary
  #
  return json.loads(subprocess.check_output([constants.IDL_TO_JSON_EXECUTABLE, filename]))

#--------------END OF UTIL ------------




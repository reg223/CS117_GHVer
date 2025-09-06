#!/bin/env python3
# rpcgenerate.py
# 

# A program that generates cpp proxy and stub files for a list of functions 
# provided in an .idl file, from command line arguments.

#   Usage: (in root directory) ../rpcgenerate <.idl source file>

#  To compile the created files, run make <filename_of_provided_idl>server or client;

# Note that compilation assumes also <filename_of_provided_idl>.cpp, which 
# contains implementation of the functions, and 
# <filename_of_provided_idl>client.cpp, which contains usage of these functions.

# The resulting RPC program is intended to use in CS117 VMs which communicates 
# through a simulated TCP socket. The program's communication is done though 
# sending bulk messages (all params/all return objects) sent at once.

# The design has accounted for endianness change of int and floats, as well as 
# sending binary strings that are not terminated by null characters.

#BY: Sam Hu and David Chen
import sys


import utils
import proxy
import stub


def generate(fname,funcDict, typeDict):
    with open("./"+fname+".proxy.cpp","w") as f:
      f.write(proxy.makeProxy(fname, funcDict, typeDict))
    with open("./"+fname+".stub.cpp","w") as f:
      f.write(stub.makeStub(fname, funcDict, typeDict))


def main():
    # get function and type declarations
    decl = utils.get_types_and_functions()
    funcDict = decl['functions']
    typeDict = decl['types']

    # generate C++ code
    generate(sys.argv[1][:-4],funcDict, typeDict)
    
if __name__ == '__main__':
    main()
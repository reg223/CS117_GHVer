# stub.py
# Functions for constructing *.stub.cpp files. Makes extensive use of 
# functions from utils.py.

# The stub template can be broken down into two major sectors: the dispatch 
# functions, which handles retrieval of parameters from proxy and their 
# reconstruction, and stub functions, which calls the function implementation 
# and compiles the returned object to buffer and sends it back.

#BY: Sam Hu and David Chen

import constants
import utils



def makeStub(fname, funcDict, typeDict)->str:
  stubTemp = utils.load_template(constants.TEMP_DIR+constants.STUB_TEMPLATE)
  return stubTemp.format(fname = fname, stubFuncs = makeStubFunc(funcDict, typeDict), dispatchCases = makeStubDispatch(funcDict,typeDict))

def makeStubFunc(funcDict, typeDict) -> str:
  stubs = []
  template = utils.load_template(constants.TEMP_DIR+constants.FUNCSTUB_TEMPLATE)

  for funcName, funcInfo in funcDict.items():
    funcHeader = utils.gen_funcHeader("__"+funcName, funcInfo)

    if funcInfo["return_type"] != "void":
      retrieveRes = utils.callFunc(funcName,funcInfo)
      updateSize = utils.gen_getSize([funcInfo["return_type"]], typeDict, "res")
      fillBuffer = utils.gen_writeSend([funcInfo["return_type"]],typeDict, "res")


    else:
      retrieveRes = f"""{funcName}({", ".join([arg["name"] for arg in funcInfo["arguments"]])});\n"""
      updateSize = """sendsize = sizeof("__Done");"""
      fillBuffer = """memcpy(sendBuff+offset,"__Done",sizeof("__Done"));\n """

      # No need to update offset for void func

    stubs.append(template.format(
    funcHeader = funcHeader,
    retrieveRes = retrieveRes,
    updateSize = updateSize,
    fillBuffer = fillBuffer
    ))
  return "\n".join(stubs)


def makeStubDispatch(funcDict, typeDict) -> str:
  dispatches = []
  template = utils.load_template(constants.TEMP_DIR+constants.DISPATCH_TEMPLATE)

  for funcName, funcInfo in funcDict.items():
      # no need to differentiate from void funcs
    arguments = funcInfo["arguments"]
    paramDeclaration = utils.paramDec(arguments)
    fillParams = utils.fillParam(arguments, typeDict)
    callStub = f"""
    __{funcName}({", ".join([arg["name"] for arg in arguments])});\n
    """
    trivialDec = utils.getTrivialDec(arguments)
      # No need to update offset for void func

    dispatches.append(template.format(
    funcname = funcName,
    paramDeclaration = paramDeclaration,
    fillParams = fillParams,
    callStub = callStub,
    trivialDec = trivialDec
    ))
    
    # each instance of the dispatch template is an if statement block, so it 
    # can naturally be connected with " else " to form an if-elseif chain.
  return " else ".join(dispatches) 


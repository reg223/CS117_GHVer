# proxy.py
# Functions for constructing *.proxy.cpp files. Makes extensive use of 
# functions from utils.py.

# The proxy template is effectively a header and a chain of proxy functions.
# This is also how proxy.py is organized.

#BY: Sam Hu and David Chen
import constants
import utils

def makeProxy(fname,funcDict,typeDict) -> str:

  proxyTemp = utils.load_template(constants.TEMP_DIR+constants.PROXY_TEMPLATE)
  return proxyTemp.format(fname = fname,functions = makeProxyFunc(funcDict,typeDict))

def makeProxyFunc(funcDict, typeDict) -> str:
  proxy = ""
  template = utils.load_template(constants.TEMP_DIR+constants.FUNCPROXY_TEMPLATE)

  for funcName, funcInfo in funcDict.items():
    funcHeader = utils.gen_funcHeader(funcName, funcInfo)
    getSize = utils.gen_getSize(funcInfo["arguments"], typeDict)
    sendHeader = utils.gen_sendHeader(funcName)
    writeSend = utils.gen_writeSend(funcInfo["arguments"], typeDict)
    if funcInfo["return_type"] != "void":
      fillInstance = utils.fillInstance(funcInfo["return_type"], typeDict, "res", "i")
      returnType = funcInfo["return_type"]
      res = "res"

    else:
      fillInstance = utils.fillInstance("stringvoid",typeDict,"res","i")
      returnType = "string"
      res = ""

    proxy += template.format(
        funcName = funcName,
        funcHeader = funcHeader,
        getSize = getSize,
        sendHeader = sendHeader,
        writeSend = writeSend,
        returnType = returnType,
        fillInstance = fillInstance,
        res = res
    ) + "\n"


  return proxy



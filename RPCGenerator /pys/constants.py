# Paths
TEMP_DIR = "./templates/"
FUNCPROXY_TEMPLATE = "proxyFuncTemp.cpp"
STUB_TEMPLATE = "stubTemp.cpp"
PROXY_TEMPLATE = "proxyTemp.cpp"
FUNCSTUB_TEMPLATE = "stubFuncTemp.cpp"
DISPATCH_TEMPLATE = "stubDispatchTemp.cpp"

# Atomic types
ATOMIC_TYPES = ["int", "void", "float"]

# Reusable templates
FOR_TEMP = """
for (int {idx} = 0; {idx} < {number}; {idx}++) {{
{repetition}
}}
"""
IDL_TO_JSON_EXECUTABLE = "./idl_to_json"
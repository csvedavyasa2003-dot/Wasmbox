from compiler import run_python_plugin

result = run_python_plugin("x = 5 + 7\nprint('Result:', x)")
print("Valid code:", result)

bad_result = run_python_plugin("this is not valid python !!!")
print("Invalid code:", bad_result)

restricted_result = run_python_plugin("import os\nos.listdir('/')")
print("Restricted import:", restricted_result)

print("Empty code:", run_python_plugin(""))
print("Huge code:", run_python_plugin("x=1\n" * 20000))
print("eval attempt:", run_python_plugin("eval('1+1')"))
print("open attempt:", run_python_plugin("open('/etc/passwd').read()"))
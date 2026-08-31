from compiler import run_python_plugin

result = run_python_plugin("x = 5 + 7\nprint('Result:', x)")
print("Valid code:", result)

bad_result = run_python_plugin("this is not valid python !!!")
print("Invalid code:", bad_result)
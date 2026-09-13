import wasmtime 

engine=wasmtime.Engine()
store=wasmtime.Store(engine)
print("wasmtime engine created successfully:", engine)
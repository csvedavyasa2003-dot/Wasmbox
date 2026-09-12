(module
  (memory 1 1000)

  (func (export "add") (param i32 i32) (result i32)
    i32.const 200
    memory.grow
  )
)

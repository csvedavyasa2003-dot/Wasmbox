(module
  (func $run (param i32) (param i32)
    (loop
      br 0
    )
  )
  (export "add" (func $run))
)

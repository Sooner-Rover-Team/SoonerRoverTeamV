# Drill Controller
 ## Bindings
 Actuator - Left stick Y axis

 Fan speed - A/B (South/East) buttons to accelerate and decelerate, 
 respectively

 Drill speed - X/Y (West/North) buttons to accelerate and decelerate, respectively

 Front triggers (left or right doesn't matter) - Reset fan speed

 Back triggers (left or right doesn't matter) - Reset drill speed

 Direction - Bound to DPad buttons. Up for 1, right for 2, released for 0.


 # Running without compiling
 There's a chance your system can just run the binary in `/target/release/drill_controller`

 If you cannot you need to...
 # Compile from source and run
 Following the steps on [the Rust-lang website](https://www.rust-lang.org/tools/install), 
 execute 

```shell
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
```

and do what it says to

Once rust is installed, you can execute `cargo run` from the `/udp_mc_drill` directory (the `Cargo.toml` file *must* be in the directory you execute `cargo run` from, which is why you need to be in `/udp_mc_drill` to run it).
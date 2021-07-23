# Remote Control
This is a newer remote control program written in Rust.
Rust was chosen with the hopes that dependency management would be way easier than the issues that Python created.

# Building - Requires Rust to be installed
To build the program, execute `$ cargo build --release`.
The binary will be placed in `./target/release/rover_controller`.
You can run that binary as normal or execute `$ cargo run` to build and run all in one step

# Running the prebuilt binary
This repository tracks the `target` directory as I develop and test the program. This means that there is a prebuilt binary in the target directory.
While building for development, the binary is built at `./target/debug/rover_controller`, so this location will always be the latest revision. `./target/release/rover_controller` includes a binary with some compiler optimizations and such, which may or may not be desirable. It's a better bet to run the executable in the `./target/debug/` directory because the executable in `./target/release/` will only be built if I remember to build it, and the `./target/debug/` directory will have the binary whether I remember or not.

# Configuration
The config file only needs a single line, in the format
`target=[ARDUINO_IP]:[PORT]`. If the config file is missing or malformed, a default will be used. This default is (as of v0.9.0) `target=192.168.1.101:1237`, which should work with the arduino as it stands at the time of writing.
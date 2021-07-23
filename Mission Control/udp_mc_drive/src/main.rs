use gilrs::{Axis, Button, Event, Gamepad, Gilrs};
use std::{collections::HashMap, convert::TryInto, fs};
use std::{net::UdpSocket, time::SystemTime};

const DEFAULT_CONFIG: &str = "target=10.0.0.1:1001";

fn alert_about_malformed_config(message: &str) {
    println!("\n\n-----------------");
    println!("{}", message);
    println!("The config should be a single line as folows: ");
    println!("\ttarget=ARDUINO_IP:PORT");
    println!("Will assume default, which is {}", &DEFAULT_CONFIG);
    println!("-----------------\n");
}

//Given the map of axes to their positions, and an axis you want
//Will retrieve the corresponding joystick position from the map,
//And if the number is negative, will subtract it from 256 to
//send the two's complement instead

fn to_twos_complement(n: i32) -> u8 {
    if n < 0 {
        return (256 + n) as u8;
    }
    return n as u8;
}

#[allow(overflowing_literals)]
fn get_i32_motor_value(axis: Axis, map: &HashMap<&Axis, f32>) -> i32 {
    let motor_value = (map.get(&axis).unwrap_or(&0.0) * 90.0).floor() as i32;
    
    return motor_value;
}

fn calculate_gimbal_value(gamepad: Gamepad, positive_button: Button, negative_button: Button) -> i32 {
    let mut value = 0;

    if gamepad.is_pressed(positive_button) {
        value += 1;
    }

    if gamepad.is_pressed(negative_button) {
        value -= 1;
    }

    return value;
}

fn calculate_modifiers(gamepad: Gamepad) -> i32{
    let axle_break_bit: i32 = gamepad.is_pressed(Button::South) as i32;
    let front_wheels_only_bit: i32 = (gamepad.is_pressed(Button::RightTrigger) || gamepad.is_pressed(Button::LeftTrigger)) as i32;
    let back_wheels_only_bit: i32 = (gamepad.is_pressed(Button::RightTrigger2) || gamepad.is_pressed(Button::LeftTrigger2)) as i32;
    let reset_camera_bit: i32 = gamepad.is_pressed(Button::Mode) as i32;


    return 1 * axle_break_bit + 2 * front_wheels_only_bit + 4 * back_wheels_only_bit + 8 * reset_camera_bit;
}

fn main() {
    let mut gilrs = Gilrs::new().unwrap();

    let config_file = fs::read_to_string("./udp_mc_drive.conf");
    let mut config_file = match config_file {
        Ok(data) => data.trim().to_string(),
        Err(err) => match err.kind() {
            std::io::ErrorKind::NotFound => {
                println!("Could not find config file, writing one and initializing with default");
                fs::write("./udp_mc_drive.conf", &DEFAULT_CONFIG).unwrap();
                fs::read_to_string("./udp_mc_drive.conf").unwrap()
            }
            _ => {
                panic!("Unknown error: {:?}", err.kind())
            }
        },
    };

    let num_lines_in_config_file = config_file.lines().count();
    if num_lines_in_config_file > 1 {
        alert_about_malformed_config(
            "The config file is more than one line\nYou are most likely using an old config",
        );
        config_file = DEFAULT_CONFIG.to_string();
    }

    println!("Config file reads: {:#?}", config_file);
    match config_file.find("target=") {
        Some(index) => {
            if index != 0 {
                alert_about_malformed_config(
                    "Cannot find target in config file. Make sure there are no spaces.",
                );
            }
            "target=".len()
        }
        None => {
            alert_about_malformed_config(
                "Cannot find target in config file. Make sure there are no spaces.",
            );
            "target=".len()
        }
    };

    let split_config: Vec<&str> = config_file
        .strip_prefix("target=")
        .unwrap()
        .split(":")
        .collect();
    let arduino_ip = split_config
        .get(0)
        .expect("Could not find ip from split confi");
    let arduino_port = split_config
        .get(1)
        .expect("Could not find port from split config");
    println!("Will send to {}:{}", arduino_ip, arduino_port);

    // Iterate over all connected gamepads
    for (_id, gamepad) in gilrs.gamepads() {
        println!("Using controller: {:?}", gamepad.name());
    }

    let mut active_gamepad = None;

    let mut time_of_last_send = SystemTime::now();

    let socket = UdpSocket::bind("0.0.0.0:43257").expect("Couldn't bind to addr");

    loop {
        // Examine new events
        while let Some(Event {
            id,
            event: _,
            time: _,
        }) = gilrs.next_event()
        {
            // println!("{:?} New event from {}: {:?}", time, id, event);
            active_gamepad = Some(id);
            continue;
        }

        if let Some(gamepad) = active_gamepad.map(|id| gilrs.gamepad(id)) {
            let axes = [
                Axis::RightStickY,
                Axis::RightStickX,
                Axis::LeftStickY,
                Axis::LeftStickX,
            ];

            //creates a map from each axis to its value
            let mut map = HashMap::new();

            for axis in axes.iter() {
                if let Some(data) = gamepad.axis_data(axis.to_owned()) {
                    if data.value().abs() > 0.1 {
                        // println!("{:#?}: {}", axis, data.value());
                        map.insert(axis, data.value());
                    } else {
                        map.insert(axis, 0.0);
                    }
                }
            }

            //sends a message every 100ms
            if SystemTime::now()
                .duration_since(time_of_last_send)
                .unwrap()
                .as_millis()
                > 100
            {
                time_of_last_send = SystemTime::now();
                let left_stick_y_value = map.get(&Axis::LeftStickY).unwrap_or(&0.0) * 90.0;
                let right_stick_y_value = map.get(&Axis::RightStickY).unwrap_or(&0.0) * 90.0;

                let mut unconverted_values = [
                    -127,
                    0,
                    calculate_modifiers(gamepad),
                    get_i32_motor_value(Axis::LeftStickY, &map),
                    get_i32_motor_value(Axis::RightStickY, &map),
                    calculate_gimbal_value(gamepad, Button::DPadUp, Button::DPadDown),
                    calculate_gimbal_value(gamepad, Button::DPadRight, Button::DPadLeft),
                    255, //dummy value, will be overwritten with the hash
                ];
                //this overwrite is nice so that we can reference elements of buf instead of copyf
                //pasting format_axis_to_send calls twice.
                let mut hash: i32 = unconverted_values[2] + unconverted_values[3] + unconverted_values[4] + unconverted_values[5] + unconverted_values[6];
                hash /= 5;
                unconverted_values[unconverted_values.len() - 1] = hash;
                println!(
                    "Hash is {:}, from {:}, {:}",
                    hash, left_stick_y_value, right_stick_y_value
                );
                println!(
                    "Gimbal values are tilt: {:}, pan: {:}",
                    unconverted_values[5], unconverted_values[6]
                );

                println!("{:#06b}", unconverted_values[2]);

                let mapped_vec: Vec<u8> = unconverted_values.iter().map(|&x| to_twos_complement(x)).collect();
                let converted_message: [u8; 8] = mapped_vec.try_into().unwrap_or([0; 8]);


                // println!("{:#?}", converted_message);

                socket
                    .send_to(&converted_message, format!("{}:{}", arduino_ip, arduino_port))
                    .expect("Couldn't send data");
            }
        }
    }
}

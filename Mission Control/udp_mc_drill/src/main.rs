use gilrs::{Axis, Button, Event, Gamepad, Gilrs};
use std::{collections::HashMap, convert::TryInto, fs};
use std::{net::UdpSocket, time::SystemTime};

const DEFAULT_CONFIG: &str = "target=10.0.0.1:1003";

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

fn get_actuator_value(map: &HashMap<&Axis, f32>) -> i32 {
    (map.get(&Axis::LeftStickY).unwrap_or(&0.0) * 90.0).floor() as i32
}

fn compute_direction(gamepad: &Gamepad) -> i32 {
    if gamepad.is_pressed(Button::DPadLeft) {
        return 0;
    }

    if gamepad.is_pressed(Button::DPadUp) {
        return 1;
    }

    if gamepad.is_pressed(Button::DPadRight) {
        return 2;
    }

    return 0;
}

fn main() {
    let mut gilrs = Gilrs::new().unwrap();

    let config_file = fs::read_to_string("./udp_mc_drill.conf");
    let mut config_file = match config_file {
        Ok(data) => data.trim().to_string(),
        Err(err) => match err.kind() {
            std::io::ErrorKind::NotFound => {
                println!("Could not find config file, writing one and initializing with default");
                fs::write("./udp_mc_drill.conf", &DEFAULT_CONFIG).unwrap();
                fs::read_to_string("./udp_mc_drill.conf").unwrap()
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

    let mut fan_speed: f32 = 0.0;
    let mut drill_speed: f32 = 0.0;

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

                //crucial that this computation is done during the send loop
                //incrementing outside the 100ms loop would max the value super quickly
                //it could also have the added effect of making it so that the drill will
                //accelerate faster proportional to the speed of your processor
                //which seems pay to win

                const BUTTON_INCREMENT: f32 = 3.0;
                if gamepad.is_pressed(Button::North) {
                    fan_speed += BUTTON_INCREMENT;
                    fan_speed = fan_speed.min(126.0)
                }
                if gamepad.is_pressed(Button::West) {
                    fan_speed -= BUTTON_INCREMENT;
                    fan_speed = fan_speed.max(-126.0)
                }

                if gamepad.is_pressed(Button::East) {
                    drill_speed += BUTTON_INCREMENT;
                    drill_speed = drill_speed.min(126.0)
                }
                if gamepad.is_pressed(Button::South) {
                    drill_speed -= BUTTON_INCREMENT;
                    drill_speed = drill_speed.max(-126.0)
                }


                if gamepad.is_pressed(Button::RightTrigger) || gamepad.is_pressed(Button::LeftTrigger) {
                    fan_speed = 0.0;
                }
                if gamepad.is_pressed(Button::RightTrigger2) || gamepad.is_pressed(Button::LeftTrigger2) {
                    drill_speed = 0.0;
                }

                time_of_last_send = SystemTime::now();

                let mut unconverted_values = [
                    -127,
                    2,
                    compute_direction(&gamepad),
                    get_actuator_value(&map),
                    drill_speed as i32,
                    fan_speed as i32,
                    255, //dummy value, will be overwritten with the hash
                ];
                //this overwrite is nice so that we can reference elements of buf instead of copyf
                //pasting format_axis_to_send calls twice.
                let mut hash: i32 = unconverted_values[2]
                    + unconverted_values[3]
                    + unconverted_values[4]
                    + unconverted_values[5];
                hash /= 4;
                unconverted_values[unconverted_values.len() - 1] = hash;
                println!("Hash is {:}", hash);
                println!("{:#?}", unconverted_values);

                let mapped_vec: Vec<u8> = unconverted_values
                    .iter()
                    .map(|&x| to_twos_complement(x))
                    .collect();
                let converted_message: [u8; 7] = mapped_vec.try_into().unwrap_or([0; 7]);

                println!("{:#?}", converted_message);

                socket
                    .send_to(
                        &converted_message,
                        format!("{}:{}", arduino_ip, arduino_port),
                    )
                    .expect("Couldn't send data");
            }
        }
    }
}

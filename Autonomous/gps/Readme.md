# GPS stuff

Gonna keep this updated as a working log of what I'm doing in the gps folder

---

## Current build and run instructions

navigate to gps and run  

```bash
mkdir build && cd build
```

then do  

```bash
cmake ..
```

followed by  

```bash
make
```

and run with  

```bash
./gps_read
```

---

## Todo List

- [x] Copy gps code over
- [x] Figure out what is necessary to running the code and what can be disposed of (bye bye cpp and hpp files)
- [x] Write a main function that can call gps methods just to see if the damn thing even works
- [x] Get it all to at least build correctly[^1]
- [ ] Figure out how to wrap the gps code and turn it into a python module
- [ ] See if that module can be imported into another python script and the correct information from the Swift can be accesssed 

[^1]: for now lmao

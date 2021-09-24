## Update 10/29/19

Added a cmake to this directory that creates the library "gps" which can be linked in another directory's cmake. However, the variables in gps.h had to be externed for this to work.

## TCP example in C for libsbp

GPS starting place: As of 10/13/18 is an example of receiving coordinates and some other stuff via TCP/IP from the Piksi. The test program simply prints out the values of the coordinates structs, but demonstrating that they're accessable is the important part. Uses C mutexes. I attempted to compile using G++ and gps.cpp and gps.hpp (with appropriate changes for C++) and am getting a couple of bugs - Someone with more knowledge about this should totally have a look and make changes.

## Requirements
On Debian-based systems (including Ubuntu 12.10 or later) you can get all
the requirements with:

```shell
sudo apt-get install build-essential pkg-config cmake
```

On mac:

```shell
brew install cmake
```

On other systems, you can obtain CMake from your operating system
package manager or from http://www.cmake.org/.

## Installation

Once you have the dependencies installed, simply invoke make

```shell
make
```



## Usage

```shell
./Test
usage: ./Test [-a address -p port]
```

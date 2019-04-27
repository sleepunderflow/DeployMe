# DeployMe

## About
DeployMe is an automatic configuration and deployment package for Linux and Windows. It is designed to allow for creation of easily configurable packages that when executed will extract injected files and execute requested commands in a secure way.

## Documentation
Full documentation is available as a PDF document inside the doc directory ([here](https://github.com/sleepunderflow/DeployMe/blob/master/doc/documentation.pdf))

## Parts
The package will consist of three main parts:
- Client binary
- Injector script
- Web Server (TODO)

### Client
It's a binary made in C++ that the injector appends the requested files to and that unpacks, decrypts and decompresses those files as well as connects to the web server to obtain license information and commands to execute.

### Injector 
Python script that generates all the necessary structures for the client to function correctly, injects the files, contacts the server to generate new license and uploads the list of commands to execute.

### Web Server
Most likely flask based server that will provide licensing information to the client and give encryption keys and commands that client is supposed to execute.

## Status
### Done
- Basic unpacker
- Injection of items
- Injection of hashes
- Validation of hashes for individual items

### Doing
- Additional metadata (permissions etc.)

### To Do
- hash validation for injected block as a whole
- Command execution
- Encryption
- Compression
- Licensing system
- Output collection and encryption
- Conditional execution
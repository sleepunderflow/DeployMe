@echo off
echo Building...

g++ -g -I include --std=c++14 src\client.cpp src\config.cpp src\languages.cpp -o bin\client.exe

echo Done
REM  make && copy bin\client.exe injector && cd injector && python3 injector.py client.exe && move client.exe new && cd new
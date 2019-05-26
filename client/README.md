# CLIENT

This is the client binary to which the injector is going to inject data and which when executed afterwards will extract embedded items.

## Requirements
On Linux this code requires libssl to be installed!!!

On Windows you need to have Visual Studio (preferably 2019 but you can change version to 2017, free community edition is fine)
If generated client binary when run on different machine shows that it requires some extra DLLs change the code generation runtime library mode
- In VS in Solution explorer right click on 'DeployMe' under "Solution 'DeployMe' and choose properties
- Go to Configuration Properties -> C/C++ -> Code Generation
- Change Runtime Library to Multi-Threaded (/MT)
- Recompile

(process like in [This post](https://gamedev.stackexchange.com/questions/138259/how-can-i-get-rid-of-missing-dll-problems) just different option selected)
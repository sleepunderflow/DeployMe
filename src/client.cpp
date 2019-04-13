#include <iostream>
#include "definitions/types.h"
#include "config.h"
#include "injectedValues.h"
#include <string>
#include <fstream>
#include <vector>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

#ifdef _WIN32
  // Only on Windows
  #ifdef _WIN64
    // 64-bit
    #include <Windows.h>
    #include <shellapi.h>
    #include <Shlobj.h>
  
  #else
    #error 32-bit targets not supported
  #endif

#elif __linux__
  // Linux only
  #include <linux/limits.h>  
  #include <sys/types.h>

#else
  // All the other targets (sorry BSD)
  #error Unsupported platform
#endif

// Variable declarations
config configuration;
static sInjectedConfig injectedValues;
std::vector<individualHeader> embeddedItems;
std::vector<std::streampos> embeddedItemsOffsets;

// Function declarations
void unpackEmbeddedTools(uint64_t offset);
void readEmbeddedItem(std::ifstream &client);
void printIndividualHeader(individualHeader);
void extractItem(unsigned int);
void checkForPrivileges();
std::string getExePath();
void showErrorAndExit(std::string, int);
void showError(std::string);

// Platform specific variables and functions
#ifdef _WIN64
  bool isConsoleApp = true;
  
  void getRidOfConsoleIfGUI();
#endif


int main(int argc, char** argv) {
  #ifdef _WIN64
    // If it's windows and we're running as graphical app (double click) get rid of the terminal window
    getRidOfConsoleIfGUI();
  #endif
  
  setDefaultConfig();
  
  // If any arguments were provided, extract them
  if (argc > 1) 
    extractConfig(argc, argv);

  processConfigurations();

  checkForPrivileges();

  std::cout << "Main header: " << sizeof(embeddedToolsMainHeader) << ", individual Header: "
    << sizeof(individualHeader) << std::endl;
  std::cout << configuration.texts.hello << std::endl;
  for (int i = 0; i < 0xff; i++){}
  std::cout << std::hex << injectedValues.header << '\n' << injectedValues.flags 
    << '\n' << injectedValues.injectedDataOffset << std::endl;
  if (injectedValues.flags && 1)
    unpackEmbeddedTools(injectedValues.injectedDataOffset);
  for (auto& header: embeddedItems) {
    printIndividualHeader(header);
  }
  for (unsigned int i = 0; i < embeddedItems.size(); i++) {
    extractItem(i);
  }
  return 0;
}

void unpackEmbeddedTools(uint64_t offset) {
  embeddedToolsMainHeader header;
  std::ifstream client;
  client.open(getExePath(), std::ios::in | std::ios::binary);
  client.seekg(offset);
  client.read((char *)&header, sizeof(embeddedToolsMainHeader));
  char contentHash[65];
  strncpy(contentHash, header.contentHash, 64);
  contentHash[64] = 0;
  std::cout << std::dec << "totalSize: " << header.totalSize << ", numberOfItems: " << header.numberOfItems
    << ", contentHash: " << contentHash << std::endl; 

  for (unsigned int i = 0; i < header.numberOfItems; i++) {
    readEmbeddedItem(client);
  }
  client.close();
}

void readEmbeddedItem(std::ifstream &client) {
  individualHeader header;
  // std::streampos start = client.tellg();
  client.read((char*)&header, sizeof(individualHeader));
  std::streampos pos = client.tellg();
  embeddedItemsOffsets.push_back(pos);
  pos += header.length - sizeof(individualHeader);
  client.seekg(pos);
  embeddedItems.push_back(header);
}

void printIndividualHeader(individualHeader header) {
  char permissions[4];
  permissions[3] = 0; 
  strncpy(permissions, header.permissions, 3);
  char itemHash[65];
  strncpy(itemHash, header.itemHash, 64);
  itemHash[64] = 0;
  char fileName[65];
  strncpy(fileName, header.fileName, 64);
  fileName[64] = 0;
  std::cout << std::dec << "Id: " << header.ID << ", length: " << header.length << ", flags: " 
    << header.flags << ", file name: " << fileName << ", item hash: " 
    << itemHash << ", permissions: " << permissions << std::endl;
}

void extractItem(unsigned int id) {
  std::ifstream client;
  client.open(getExePath(), std::ios::in | std::ios::binary);

  individualHeader header = embeddedItems[id];
  std::streampos offset = embeddedItemsOffsets[id];
  client.seekg(offset);
  char* buffer = (char*) malloc(header.length);
  client.read(buffer, header.length - sizeof(individualHeader));

  char fileName[65];
  strncpy(fileName, header.fileName, 64);
  fileName[64] = 0;

  std::fstream output(fileName, std::ios::out | std::ios::binary);
  output.write(buffer, header.length - sizeof(individualHeader));

  free(buffer);
  client.close();
  output.close();
}

std::string getExePath() {
  char result[ PATH_MAX ];
  #ifdef __linux__
    ssize_t count = readlink( "/proc/self/exe", result, PATH_MAX );
  #elif _WIN64
    int count = GetModuleFileNameA(nullptr, result, PATH_MAX);
  #endif
  return std::string( result, (count > 0) ? count : 0 );
}

#ifdef _WIN64
  // FROM https://stackoverflow.com/questions/8046097/how-to-check-if-a-process-has-the-administrative-rights
  BOOL IsElevated( ) {
    BOOL fRet = FALSE;
    HANDLE hToken = NULL;
    if( OpenProcessToken( GetCurrentProcess( ),TOKEN_QUERY,&hToken ) ) {
        TOKEN_ELEVATION Elevation;
        DWORD cbSize = sizeof( TOKEN_ELEVATION );
        if( GetTokenInformation( hToken, TokenElevation, &Elevation, sizeof( Elevation ), &cbSize ) ) {
            fRet = Elevation.TokenIsElevated;
        }
    }
    if( hToken ) {
        CloseHandle( hToken );
    }
    return fRet;
  }
#endif

void checkForPrivileges() {
  // If elevate privileges bit is not set just ignore
  if ((injectedValues.flags & 4) == 0)
    return;

  #ifdef __linux__
    // If not being run as root then exit
    if (getuid() != 0) 
      showErrorAndExit("This program must be run as root!", -1);
  #elif _WIN64
    bool isAdmin = IsElevated();
    if (!isAdmin) {
      // Launch itself as administrator. 
      wchar_t szPath[MAX_PATH]; 
      if (!GetModuleFileName(NULL, (LPSTR)szPath, ARRAYSIZE(szPath)))
        showErrorAndExit("Something went wrong!", -1);

      SHELLEXECUTEINFO sei = { sizeof(sei) }; 
      sei.lpVerb = (LPCSTR)"runas"; 
      sei.lpFile = (LPCSTR)szPath; 
      sei.lpParameters = (LPCSTR)("-l " + configuration.lang).c_str();
      sei.hwnd = GetActiveWindow(); 
      sei.nShow = SW_NORMAL | SEE_MASK_NOASYNC | SW_RESTORE  | SW_SHOW ; 

      if (!ShellExecuteEx(&sei)) 
        showErrorAndExit("This program must be run as administrator!", -1);
      else 
        // The child is going to take over now
        exit(0);
    }
  #endif
}

#ifdef _WIN64
  void getRidOfConsoleIfGUI() {
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    // Get handle to the console info
    HANDLE hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
    if (!GetConsoleScreenBufferInfo(hStdOutput, &csbi))
      showError("GetConsoleScreenBufferInfo failed");
    // if cursor position is (0,0) then we are running as GUI
    if ((!csbi.dwCursorPosition.X) && (!csbi.dwCursorPosition.Y)) {
      // In that case just get rid of the console window and set the flag
      isConsoleApp = false;
      FreeConsole();
    }
  }
#endif 

void showErrorAndExit(std::string message, int exitCode) {
  showError(message);
  exit(exitCode);
}

void showError(std::string message) {
  #ifdef _WIN64
    // If it's windows and GUI application then show message box, otherwise do what linux does
    if (!isConsoleApp)
      MessageBox(NULL,message.c_str(),"ERROR",MB_OK|MB_ICONERROR);
    else
  #endif
  {
    std::cerr << message << std::endl; 
  }
}
#include <iostream>
#include "definitions/types.h"
#include "definitions/constants.h"
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
void readEmbeddedToolInformation(uint64_t offset);
void readEmbeddedItem(std::ifstream &client);
void printIndividualHeader(individualHeader);
void extractItem(unsigned int);
void checkForPrivileges();
std::string getExePath();
void showErrorAndExit(std::string, int);
void showError(std::string);
void checkIfReadSuccessful(std::istream&);

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

  // Display welcome line in a correct language
  std::cout << configuration.texts.hello << std::endl;

  // Display information about injected values
  std::cout << std::hex << "Header: " << injectedValues.header 
    << "\nFlags: " << injectedValues.flags 
    << "\nOffset of injected data " << injectedValues.injectedDataOffset 
    << std::endl;

  // If the flag says that there exist embedded data, unpack them
  if (injectedValues.flags && FLAG_EMBEDPRESENT)
    readEmbeddedToolInformation(injectedValues.injectedDataOffset);

  for (auto& header: embeddedItems) {
    printIndividualHeader(header);
  }
  for (unsigned int i = 0; i < embeddedItems.size(); i++) {
    extractItem(i);
  }

  return 0;
}

/*
* Arguments: 
* - uint64_t offset - offset at which the embedded files start
*
* This function tries to read the main header for embedded items and 
*   calls functions filling structures for each of the embedded files
*/
void readEmbeddedToolInformation(uint64_t offset) {
  embeddedToolsMainHeader header;
  std::ifstream client;
  char contentHash[65] = {0};

  // Open itself as a file for reading in binary mode
  client.open(getExePath(), std::ios::in | std::ios::binary);
  client.seekg(offset);
  client.read((char *)&header, sizeof(embeddedToolsMainHeader));
  checkIfReadSuccessful(client);

  // Unpack the hash (probably is not NULL-terminated so can't just use it as a string directly)
  strncpy(contentHash, header.contentHash, 64);

  std::cout << std::dec << "totalSize: " << header.totalSize 
    << ", numberOfItems: " << header.numberOfItems
    << ", contentHash: " << contentHash 
    << std::endl; 

  // Process every injected item up to the specified number of items
  for (unsigned int i = 0; i < header.numberOfItems; i++) {
    readEmbeddedItem(client);
  }

  client.close();
}


/*
 * Arguments:
 * - std::ifstream &client - opened file object from which to read
 *   the item information - variable state will be modified
 *
 * This function reads the embedded item information from the file
 *   pushes the obtained header to the global vector object 
 *   and advances the file state to right after the current embedded item
 *
 * Modified global objects:
 * - embeddedItems - added data
 * - embeddedItemsOffsets - added data
 */
void readEmbeddedItem(std::ifstream &client) {
  individualHeader header;
  // Read the header without extra data
  client.read((char*)&header, sizeof(individualHeader)-sizeof(header.additionalData));
  checkIfReadSuccessful(client);

  int metadataSize = header.headerLength-144;

  header.additionalData = (char*)malloc(metadataSize + 1);
  if (header.additionalData == nullptr) {
    showErrorAndExit("Can't allocate memory for item metadata", -2);
  }
  
  header.additionalData[metadataSize] = 0;
  client.read(header.additionalData, metadataSize);

  embeddedItems.push_back(header);
  // Get the current position in the file and push it to the vector
  std::streampos pos = client.tellg();
  embeddedItemsOffsets.push_back(pos);
  // Move on to the next item
  pos += header.payloadLength;
  client.seekg(pos);
}

/*
 * Arguments:
 * - individualHeader header - individualHeader object that was read 
 *   from the source file
 *
 * This function displays information that was read from the source file 
 *   as a header of embedded file
 */
void printIndividualHeader(individualHeader header) {
  /* Values are unlikely to be null-terminated so each of them has to 
  *  be individually copied over to a char array and null terminated */
  char itemHash[65] = {0};
  char fileName[65] = {0};

  strncpy(itemHash, header.itemHash, 64);
  strncpy(fileName, header.fileName, 64);

  std::cout << std::dec << "Id: " << header.ID 
    << ", payload length: " << header.payloadLength 
    << ", header length: " << header.headerLength 
    << ", flags: " << header.flags 
    << ", file name: " << fileName 
    << ", item hash: " << itemHash 
    << ", additional metadata: " << header.additionalData 
    << std::endl;
}

/*
 * Arguments: 
 * - unsigned int id: ID of an item to be unpacked
 * 
 * This function takes a numerical ID of an embedded item, goes to the corresponding 
 * offset in the executable and extracts the file to the requested file name
 */
void extractItem(unsigned int id) {
  std::ifstream client;
  client.open(getExePath(), std::ios::in | std::ios::binary);

  individualHeader header = embeddedItems[id];
  std::streampos offset = embeddedItemsOffsets[id];
  client.seekg(offset);
  char* buffer = (char*) malloc(header.payloadLength);
  client.read(buffer, header.payloadLength);
  checkIfReadSuccessful(client);

  char fileName[65];
  strncpy(fileName, header.fileName, 64);
  fileName[64] = 0;

  std::fstream output(fileName, std::ios::out | std::ios::binary);
  output.write(buffer, header.payloadLength);

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
  if (injectedValues.flags & FLAG_ELEVATE)
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

void checkIfReadSuccessful(std::istream& file) {
  if (file.fail()) {
    if (file.eof())
      showErrorAndExit("Run out of data before finished processing", ERR_NOTENOUGHDATA);
    else 
      showErrorAndExit("Unknown error while reading the source file", ERR_UNKOWNFILEERROR);
  }
}
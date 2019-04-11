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
   #ifdef _WIN64
      #include <windows.h>
   #else
      #error 32-bit targets not supported
   #endif
#elif __linux__
  #include <linux/limits.h>  
#else
  #error Unsupported platform
#endif

config configuration;

static sInjectedConfig injectedValues;
std::vector<individualHeader> embeddedItems;
std::vector<std::streampos> embeddedItemsOffsets;

void unpackEmbeddedTools(uint64_t offset);
void readEmbeddedItem(std::ifstream &client);
void printIndividualHeader(individualHeader);
void extractItem(unsigned int);
std::string getExePath();

int main(int argc, char **argv) {
  if (argc > 1) {
    setDefaultConfig();
    extractConfig(argc, argv);
    processConfigurations();
  } else {
    exit(0);
  }
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
  std::cout << std::dec << ", totalSize: " << header.totalSize << ", numberOfItems: " << header.numberOfItems
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
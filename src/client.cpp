#include <iostream>
#include "definitions/types.h"
#include "config.h"
#include "injectedValues.h"
#include <string>
#include <fstream>

config configuration;

struct sInjectedConfig injectedValues;

void unpackEmbeddedTools(uint64_t offset);

int main(int argc, char **argv) {
  if (argc > 1) {
    setDefaultConfig();
    extractConfig(argc, argv);
    processConfigurations();
  } else {
    exit(0);
  }
  std::cout << configuration.texts.hello << std::endl;
  for (int i = 0; i < 0xff; i++){}
  std::cout << std::hex << injectedValues.header << '\n' << injectedValues.flags 
    << '\n' << injectedValues.injectedDataOffset << std::endl;
  if (injectedValues.flags && 1)
    unpackEmbeddedTools(injectedValues.injectedDataOffset);
  return 0;
}

//TODO
void unpackEmbeddedTools(uint64_t offset) {
  embeddedToolsMainHeader header;
  std::fstream client;
  client.open("client", std::ios::in);
  
  client.seekg(offset);
  client.read((char *)&header, sizeof(embeddedToolsMainHeader));
  std::cout << "totalSize: " << header.totalSize << ", numberOfItems: " << header.numberOfItems
    << ", contentHash: " << header.contentHash << std::endl; 
}
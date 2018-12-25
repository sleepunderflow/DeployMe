#ifndef TYPES_H
#define TYPES_H
#include <string>
#include <iostream>

struct texts
{
  std::string hello;
};

struct embeddedToolsMainHeader {
  uint32_t totalSize;
  uint16_t numberOfItems;
  char contentHash[32];
};

struct individualHeader {
  uint16_t ID;
  uint32_t length;
  char fileName[64];
  char itemHash[32];
  char permissions[3];
};

#endif //TYPES_H

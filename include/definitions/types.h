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
  uint32_t numberOfItems;
  char contentHash[64];
};

struct individualHeader {
  uint32_t ID;
  uint32_t length;
  uint32_t flags;
  char fileName[64];
  char itemHash[64];
  char permissions[4];
};

#endif //TYPES_H

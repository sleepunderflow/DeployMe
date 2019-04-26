#ifndef TYPES_H
#define TYPES_H
#include <string>
#include <iostream>

struct texts
{
  std::string hello;
};

typedef struct {
  uint32_t totalSize;
  uint32_t numberOfItems;
  char contentHash[64];
} embeddedToolsMainHeader;

typedef struct {
  uint32_t ID;
  uint32_t headerLength;
  uint32_t payloadLength;
  uint32_t flags;
  char fileName[64];
  char itemHash[64];
  char* additionalData;
} individualHeader;

#endif //TYPES_H

#ifndef TYPES_H
#define TYPES_H
#include <string>
#include <iostream>

typedef struct{
  std::string hello;
  std::string cantAllocateMemoryMetadata;
  std::string somethingWentWrong;
  std::string thisProgramMustBeRunAsRoot;
} translation;

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

typedef struct {
  std::string permission;
} metadata;

#endif //TYPES_H

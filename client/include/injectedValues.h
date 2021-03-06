#ifndef INJECTED_VALUES_H
#define INJECTED_VALUES_H

#include <cstdint>

typedef struct {
  uint64_t header = 0xDEADBEEFDEADBEEF;
  uint64_t flags = 0x0000000000000000;
  uint64_t injectedDataOffset = 0x1111111111111111;
} sInjectedConfig;

#endif // INJECTED_VALUES_H

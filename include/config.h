#ifndef CONFIG_H
#define CONFIG_H

#include <string>
#include "types.h"

struct config {
  const char *lang;
  struct texts texts;
};

void extractConfig(int argc, char **argv);

#endif //CONFIG_H

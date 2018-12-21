#ifndef CONFIG_H
#define CONFIG_H

#include <string>
#include "definitions/types.h"

struct config {
  std::string lang;
  struct texts texts;
};

void extractConfig(int argc, char **argv);
void setDefaultConfig();
void processConfigurations();

#endif //CONFIG_H

#ifndef CONFIG_H
#define CONFIG_H

#include <string>
#include "definitions/types.h"

typedef struct {
  std::string lang;
  translation texts;
} config;

void extractConfig(int argc, char **argv);
void setDefaultConfig();
void processConfigurations();

#endif //CONFIG_H

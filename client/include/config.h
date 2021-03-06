#ifndef CONFIG_H
#define CONFIG_H

#include "definitions/types.h"
#include <string>


typedef struct {
  bool debugMode;
  std::string lang;
  translation texts;
} config;

void extractConfig(int argc, char **argv);
void setDefaultConfig();
void processConfigurations();
void showUsage(char *);

#endif // CONFIG_H

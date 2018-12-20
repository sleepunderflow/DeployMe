#include <iostream>
#include "types.h"
#include "config.h"

config configuration;

int main(int argc, char **argv) {
  if (argc > 1) {
    extractConfig(argc, argv);
  } else {
    exit(0);
  }
  std::cout << configuration.texts.hello << std::endl;
  return 0;
}
#include "config.h"
#include "types.h"

extern config configuration;

void extractConfig(int argc, char **argv) {
  for (int i = 1; i <= argc; i++) {
    if ((const char*)argv[i] == "-l" || (const char*)argv[i] == "--language") {
      if (i+1 <= argc) {
        ++i;
        configuration.lang = (const char*)argv[i];
        configuration.texts = getLanguage(configuration.lang);
      } else {
        std::cout << "Incorrect number of arguments" << std::endl;
        exit(1);
      }
    }
  }
}
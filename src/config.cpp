#include "config.h"
#include "definitions/types.h"
#include "languages.h"

extern config configuration;

void extractConfig(int argc, char **argv) {
  for (int i = 1; i < argc; i++) {
    std::string argument = std::string(argv[i]);
    if (argument == "-l" || argument == "--language") {
      if (i+1 < argc) {
        ++i;
        configuration.lang = std::string(argv[i]);
        configuration.texts = getLanguage(configuration.lang);
      } else {
        std::cout << "Incorrect number of arguments" << std::endl;
        exit(1);
      }
    }
  }
}
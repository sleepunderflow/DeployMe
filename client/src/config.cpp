#include "../include/config.h"
#include "../include/definitions/types.h"
#include "../include/languages.h"
#include "../include/errorHandling.h"

extern config configuration;

void extractConfig(int argc, char **argv) {
  // If something fails we either already have the language set by user or we have 
  // the default set so we can show the message
  for (int i = 1; i < argc; i++) {
    std::string argument = std::string(argv[i]);
    if (argument == "-l" || argument == "--language") {
      assertOrFailWithMessage((i+1 < argc), 
        "--language " + getLanguage(configuration.lang).requiresAParameter);
      ++i;
      configuration.lang = std::string(argv[i]);
      continue;
    } else if (argument == "-d") {
      configuration.debugMode = true;
      continue;
    } else if (argument == "-h") { 
      showUsage(argv[0]);
      exit(0);
    } else {
      showError(getLanguage(configuration.lang).unknownParameter + argument);
      showUsage(argv[0]);
      exit(-1);
    }
  }
}

void setDefaultConfig() {
  configuration.lang = "en_GB";
  configuration.debugMode = false;
}

void processConfigurations() {
  configuration.texts = getLanguage(configuration.lang);
}

void showUsage(char* name) {
  std::cout << 
    "Usage: " << name << " [parameters]\n\n" <<
    "Parameters:\n" <<
    "\t -l - set language, available: en_GB, pl_PL\n" <<
    "\t -d - enable debug mode\n" << 
    "\t -h - show this message and exit" << std::endl; 
}
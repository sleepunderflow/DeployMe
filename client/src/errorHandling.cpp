#include "errorHandling.h"

void showErrorAndExit(std::string message, int exitCode) {
  showError(message);
  exit(exitCode);
}

void showError(std::string message) {
  #ifdef _WIN64
    // If it's windows and GUI application then show message box, otherwise do what linux does
    if (!isConsoleApp)
      MessageBox(NULL,message.c_str(),configuration.texts.error,MB_OK|MB_ICONERROR);
    else
  #endif
  {
    std::cerr << message << std::endl; 
  }
}

void checkIfReadSuccessful(std::istream& file) {
  if (file.fail()) {
    if (file.eof())
      showErrorAndExit(configuration.texts.runOutOfData, ERR_NOTENOUGHDATA);
    else 
      showErrorAndExit(configuration.texts.unknownErrorFileProcessing, ERR_UNKOWNFILEERROR);
  }
}

void assertOrFailWithMessage(bool condition, std::string errorMessage) {
  if (condition)
    return;

  showErrorAndExit(errorMessage, ERR_ASSERTIONERROR);
}

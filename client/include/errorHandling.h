#pragma once
#include "definitions/constants.h"
#include "config.h"

#include <string>
#include <iostream>
#include <fstream>
#ifdef _WIN64
  #include <windows.h>
#endif

extern config configuration;

void showErrorAndExit(std::string, int);
void showError(std::string);
void checkIfReadSuccessful(std::istream&);
void assertOrFailWithMessage(bool, std::string);
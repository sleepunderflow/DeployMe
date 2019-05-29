#pragma once
#include "config.h"
#include "definitions/constants.h"


#include <fstream>
#include <iostream>
#include <string>

#ifdef _WIN64
#include <windows.h>
#endif

extern config configuration;

void showErrorAndExit(std::string, int);
void showError(std::string);
void checkIfReadSuccessful(std::istream &);
void assertOrFailWithMessage(bool, std::string);
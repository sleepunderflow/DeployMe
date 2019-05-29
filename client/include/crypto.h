#pragma once

#ifdef _WIN64
#include <Windows.h>
#include <bcrypt.h>

#elif __linux__
#include <cstring>
#include <openssl/evp.h>


#endif

#include "errorHandling.h"

void checkHash(char *, unsigned int, char *);

#ifdef _WIN64
void freeHashResources(BCRYPT_ALG_HANDLE &, BCRYPT_HASH_HANDLE &, PBYTE &,
                       PBYTE &);
#endif
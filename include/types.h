#ifndef TYPES_H
#define TYPES_H
#include <string>
#include <iostream>

struct texts
{
  std::string hello;
};

texts getLanguage(const char *language);
texts getLangEN_GB();
texts getLangPL_PL();

#endif //TYPES_H

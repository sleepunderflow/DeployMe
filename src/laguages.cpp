#include "types.h"

texts getLanguage(const char *language) {
  if (language == "en_GB") {
    return getLangEN_GB();
  } else if (language == "pl_PL") {
    return getLangPL_PL();
  }
  std::cout << "Unknown Language " << language << std::endl;
  exit(1);
}

texts getLangEN_GB() {
  struct texts texts_EN_GB;
  texts_EN_GB.hello = "Hello!";

  return texts_EN_GB;
}

texts getLangPL_PL() {
  struct texts texts_PL_PL;
  texts_PL_PL.hello = "Witam!";

  return texts_PL_PL;
}
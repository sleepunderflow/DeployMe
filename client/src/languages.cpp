#include "languages.h"

translation getLanguage(std::string language) {
  if (language == "en_GB") {
    return getLangEN_GB();
  } else if (language == "pl_PL") {
    return getLangPL_PL();
  }
  std::cout << "Unknown Language " << language << std::endl;
  exit(1);
}

translation getLangEN_GB() {
  translation texts_EN_GB;
  texts_EN_GB.hello = "Hello!";
  texts_EN_GB.cantAllocateMemoryMetadata = "Can't allocate memory for item metadata";
  texts_EN_GB.somethingWentWrong = "Something went wrong!";
  texts_EN_GB.thisProgramMustBeRunAsRoot = "This program must be run as root!";

  return texts_EN_GB;
}

translation getLangPL_PL() {
  // Use en_GB as base so that if something is not translated it'll be displayed in english
  translation texts_PL_PL = getLangEN_GB();
  texts_PL_PL.hello = "Witam!";
  texts_PL_PL.cantAllocateMemoryMetadata = "Nie można zaalokować pamięci dla metadanych obiektu";
  texts_PL_PL.somethingWentWrong = "Coś poszło nie tak";
  texts_PL_PL.thisProgramMustBeRunAsRoot = "Ten program musi być uruchomiony jako root!";

  return texts_PL_PL;
}
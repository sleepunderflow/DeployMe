#include "../include/languages.h"

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
  translation texts;
  texts.hello = "Hello!";
  texts.cantAllocateMemoryMetadata = "Can't allocate memory for item metadata";
  texts.somethingWentWrong = "Something went wrong!";
  texts.thisProgramMustBeRunAsRoot = "This program must be run as root!";
  texts.header = "Header";
  texts.flags = "Flags";
  texts.offsetOfInjectedData = "Offset of injected data";
  texts.incorrectNumberOfArguments =
      "Incorrect number of arguments to the program";
  texts.requiresAParameter = "option requires a parameter";
  texts.unknownParameter = "Unknown parameter ";
  texts.runOutOfData = "Run out of data before finished processing";
  texts.unknownErrorFileProcessing =
      "Unknown error while reading the source file";
  texts.error = "ERROR";
  texts.payloadLength = "payload length";
  texts.headerLength = "header length";
  texts.fileName = "File name";
  texts.itemHash = "Item hash";
  texts.additionalMetadata = "Additional metadata";
  texts.cantCreateHashFunction = "Can't create hash function";
  texts.cantGetConsoleScreenBuffer = "Can't get console screen buffer info";
  texts.itemHashDoesntMatch = "Hash of embedded item doesn't match";
  // texts. = "";

  return texts;
}

// TODO: Wide strings for Windows
translation getLangPL_PL() {
  // Use en_GB as base so that if something is not translated it'll be displayed
  // in english
  translation texts = getLangEN_GB();
  texts.hello = "Witam!";
  texts.cantAllocateMemoryMetadata =
      "Nie można zaalokować pamięci dla metadanych obiektu";
  texts.somethingWentWrong = "Coś poszło nie tak";
  texts.thisProgramMustBeRunAsRoot =
      "Ten program musi być uruchomiony jako root!";
  texts.header = "Nagłówek";
  texts.flags = "Flagi";
  texts.offsetOfInjectedData = "Lokalizacja wstrzykniętych danych w pliku";
  texts.incorrectNumberOfArguments = "Zła liczba parametrów do programu";
  texts.requiresAParameter = "wymaga dodatkowego parametru";
  texts.unknownParameter = "Nieznany parametr ";
  texts.runOutOfData = "Skończyły się dane przed końcem przetwarzania";
  texts.unknownErrorFileProcessing =
      "Nieznany błąd podczas czytania pliku źródłowego";
  texts.error = "BŁĄD";
  texts.payloadLength = "Długość danych";
  texts.headerLength = "Długość nagłówka";
  texts.fileName = "Nazwa pliku";
  texts.itemHash = "Hash obiektu";
  texts.additionalMetadata = "Dodatkowe metadane";
  texts.cantCreateHashFunction = "Nie można utworzyć funkcji hashującej";
  texts.cantGetConsoleScreenBuffer =
      "Nie można uzyskać informacji o buforze konsoli";
  texts.itemHashDoesntMatch = "Hash dodanego obiektu się nie zgadza";

  return texts;
}
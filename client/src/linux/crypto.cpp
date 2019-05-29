#ifdef __linux__

#include "../../include/crypto.h"

void checkHash(char *data, unsigned int length, char *expectedHash) {
  unsigned char md_value[EVP_MAX_MD_SIZE];
  unsigned int md_len;
  const EVP_MD *md = EVP_sha256();
  if (md == NULL)
    showErrorAndExit(configuration.texts.cantCreateHashFunction,
                     ERR_INTERNALHASHERPROBLEM);
  EVP_MD_CTX *mdctx;
  mdctx = EVP_MD_CTX_new();
  EVP_DigestInit_ex(mdctx, md, NULL);
  EVP_DigestUpdate(mdctx, data, length);
  EVP_DigestFinal_ex(mdctx, md_value, &md_len);
  EVP_MD_CTX_free(mdctx);

  char hexdigest[65] = {0};
  for (unsigned int i = 0; i < md_len; i++)
    sprintf(hexdigest + i * 2, "%02x", md_value[i]);

  if (strncmp(hexdigest, expectedHash, 64) != 0)
    showErrorAndExit(configuration.texts.itemHashDoesntMatch,
                     ERR_ITEMHASHDONTMATCH);
}
#endif
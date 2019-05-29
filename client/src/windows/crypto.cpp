#ifdef _WIN64

#include "../../include/crypto.h"

// Magic from Microsoft docs for hashing
#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)
#define STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)

void freeHashResources(BCRYPT_ALG_HANDLE &hAlg, BCRYPT_HASH_HANDLE &hHash,
                       PBYTE &pbHashObject, PBYTE &pbHash) {
  if (hAlg)
    BCryptCloseAlgorithmProvider(hAlg, 0);
  if (hHash)
    BCryptDestroyHash(hHash);
  if (pbHashObject)
    HeapFree(GetProcessHeap(), 0, pbHashObject);
  if (pbHash)
    HeapFree(GetProcessHeap(), 0, pbHash);
}

void __failHash(BCRYPT_ALG_HANDLE &hAlg, BCRYPT_HASH_HANDLE &hHash,
                PBYTE &pbHashObject, PBYTE &pbHash) {
  freeHashResources(hAlg, hHash, pbHashObject, pbHash);
  showErrorAndExit(configuration.texts.cantCreateHashFunction,
                   ERR_INTERNALHASHERPROBLEM);
}

void checkHash(char *data, unsigned int length, char *expectedHash) {
  BCRYPT_ALG_HANDLE hAlg = NULL;
  BCRYPT_HASH_HANDLE hHash = NULL;
  DWORD cbData = 0, cbHash = 0, cbHashObject = 0;
  PBYTE pbHashObject = NULL;
  PBYTE pbHash = NULL;
  NTSTATUS result;

  // open sha256 provider
  if (!NT_SUCCESS(
          BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_SHA256_ALGORITHM, NULL, 0)))
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  // Get hash object size
  if (!NT_SUCCESS(BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH,
                                    (PBYTE)&cbHashObject, sizeof(DWORD),
                                    &cbData, 0)))
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  // Allocate memory for hash object
  pbHashObject = (PBYTE)HeapAlloc(GetProcessHeap(), 0, cbHashObject);
  if (pbHashObject == NULL)
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  // Get the hash length
  if (!NT_SUCCESS(result = BCryptGetProperty(hAlg, BCRYPT_HASH_LENGTH,
                                             (PBYTE)&cbHash, sizeof(DWORD),
                                             &cbData, 0)))
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  // Allocate memory for hash buffer
  pbHash = (PBYTE)HeapAlloc(GetProcessHeap(), 0, cbHash);
  if (pbHashObject == NULL)
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  // Create hash
  if (!NT_SUCCESS(BCryptCreateHash(hAlg, &hHash, pbHashObject, cbHashObject,
                                   NULL, 0, 0)))
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  // Hash data, finally
  if (!NT_SUCCESS(BCryptHashData(hHash, (PBYTE)data, length, 0)))
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  if (!NT_SUCCESS(BCryptFinishHash(hHash, pbHash, cbHash, 0)))
    __failHash(hAlg, hHash, pbHashObject, pbHash);

  char hexdigest[65] = {0};
  for (unsigned int i = 0; i < cbHash; i++)
    sprintf(hexdigest + i * 2, "%02x", pbHash[i]);

  freeHashResources(hAlg, hHash, pbHashObject, pbHash);

  if (strncmp(hexdigest, expectedHash, 64) != 0)
    showErrorAndExit(configuration.texts.itemHashDoesntMatch,
                     ERR_ITEMHASHDONTMATCH);
}
#endif
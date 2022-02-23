"""Define paths, URL's, etc."""
import sys
def setup_paths():
    PUBLISH0X_REPO = "/home/johnrangel/Projects/crypto-publish0x"
    CRYPTO_API_LIBRARY = "%s/crypto-api"%PUBLISH0X_REPO
    for PATH in [
        PUBLISH0X_REPO,
        CRYPTO_API_LIBRARY,
        ]:
        sys.path.append(PATH)

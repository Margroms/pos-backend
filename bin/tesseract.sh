#!/bin/bash
# Add our custom bin directory to the PATH for this execution
export PATH="/var/task/bin:$PATH"

# Set the Tesseract data prefix environment variable
export TESSDATA_PREFIX=/var/task/tessdata

# Now, execute tesseract. The system will find it in the path we just added.
exec tesseract "$@"

#!/bin/bash
export TESSDATA_PREFIX=/var/task/tessdata
exec /var/task/bin/tesseract "$@"

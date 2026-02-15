#!/bin/bash

grep "\[\[@BibleBHS:" HOTTP-PENTATEUCH.txt \
  | sed -n 's/.*\[\[BibleBHS:\([A-Z][A-Z][A-Z] [0-9]\+:[0-9]\+\)\].*/\1/p' \
  > hottp_refs.txt

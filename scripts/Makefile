# SPDX-License-Identifier: AGPL-3.0-or-later

include ../utils/makefile.include

TOPTARGETS := all clean test build

all: test
test:
  $(Q)../prj cmd msg.build TEST "scripts/.*sh"
  $(Q)shellcheck -x -s bash ./*.sh

.PHONY: $(TOPTARGETS)

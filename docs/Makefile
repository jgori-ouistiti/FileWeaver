# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

FW_PARENT_DIR=$(patsubst %/,%,$(dir $(abspath $(lastword $(shell pwd)))))
export CONFIG_FILE := $(FW_PARENT_DIR)/conf.cfg

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

whtml:
	
	rm -rf _build
	rm -rf _autosummary
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -W $(SPHINXOPTS) $(O)


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).

# Note: Jupytext converts .py to .ipynb (Sphinx seems to execute Notebook..?)
%: Makefile
	echo $$CONFIG_FILE
	rm -rf _build
	rm -rf _autosummary
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

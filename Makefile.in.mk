# -----------------------------------------------
# independent variables

#DIR_VENV := $(shell poetry --venv 2>/dev/null)


# -----------------------------------------------
# OS-depend variables

ifeq ($(OS), Windows_NT)

DIR_REPO := $(shell cd)

else

DIR_REPO := $(shell pwd)

endif


# -----------------------------------------------
# Paths

DIR_UTILS = $(DIR_REPO)/utils
DIR_SRC := $(DIR_REPO)/src
DIR_TESTS := $(DIR_REPO)/tests
DIR_DATA := $(DIR_REPO)/data

# -----------------------------------------------
# Virtualenv-depend variables

ifeq ($(shell python "$(DIR_UTILS)/detect_venv.py"), True)

IN_VENV := True
RUN :=
PIPENV_INSTALL := echo Cannot create venv under venv

else

IN_VENV := False
RUN := pipenv run
PIPENV_INSTALL := pipenv install

endif


# -----------------------------------------------
# calculated variables

PYTHON := $(RUN) python


# -----------------------------------------------
# OS-depend actions

ifeq ($(OS), Windows_NT)

define log
	@echo ">>>>>>>>>>>>>>>>    $(1)"
endef

else

define log
	@tput bold 2>/dev/null || exit 0
	@tput setab 0  2>/dev/null || exit 0
	@tput setaf 4  2>/dev/null || exit 0
	@echo ">>>>>>>>>>>>>>>>    $(1)    "
	@tput sgr0  2>/dev/null || exit 0
endef

endif

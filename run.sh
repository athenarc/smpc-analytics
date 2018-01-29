#!/bin/bash
EMU="sm_run.sh"
WD=$(pwd)
(cd ${SHAREMIND_BIN} && ${EMU} $WD/$1)


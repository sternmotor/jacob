#!/usr/bin/env bash
# <script function description >

# make script robust 
set -euo pipefail # exit on ec>0, on unset vars, in pipes
shopt -s nullglob # resolve none-existent '*' files to nothing 
export LANG=C     # haved error messages in english

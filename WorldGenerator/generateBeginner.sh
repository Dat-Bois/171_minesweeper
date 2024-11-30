#!/bin/bash

rm -rf Problems
mkdir Problems

python3 WorldGenerator.py 1000 Beg_world_ 8 8 10

echo Finished generating worlds!

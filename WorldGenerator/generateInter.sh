#!/bin/bash

rm -rf Problems
mkdir Problems

python3 WorldGenerator.py 100 Beg_world_ 16 16 40

echo Finished generating worlds!

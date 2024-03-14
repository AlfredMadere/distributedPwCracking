#!/bin/bash

find .. -name '*.py' ! -path "./.git/*" ! -path "*/__pycache__/*" -exec wc -l {} +
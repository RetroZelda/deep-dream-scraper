#!/bin/bash

number_of_pages="$1"
output_folder="$2"

python3 ./deep-dream-scraper.py -p $number_of_pages -o $output_folder

detox $output_folder/*
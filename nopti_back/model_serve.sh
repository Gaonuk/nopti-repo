#!/bin/bash


python3 -m llama_cpp.server \
    --model /Users/theomichel/Coding/Hackaton/nopti_back/llama-3.2-1b-instruct-q8_0.gguf \
    --host localhost    --port 8111
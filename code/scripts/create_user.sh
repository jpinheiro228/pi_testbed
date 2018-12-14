#!/bin/bash

useradd -G sudo -s /bin/bash -m -p $(openssl passwd -1 $1) $1

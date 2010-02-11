#!/bin/bash
ln -s /git/triagem/squash-mount.py /usr/bin/squash-mount.py
cp /git/triagem/squash-mount /etc/init.d/squash-mount
mkdir -p /etc/squash-mount
ln -s /git/triagem/squash-mount.conf /etc/squash-mount/squash-mount.conf
rc-update add squash-mount default

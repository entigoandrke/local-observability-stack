#!/usr/bin/env bash

ANSIBLE_CONFIG=./ansible.cfg ansible-playbook --inventory ./inventories/hosts site.yaml || exit 200

tail -f /dev/null
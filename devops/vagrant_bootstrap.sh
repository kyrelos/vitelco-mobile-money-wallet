#!/usr/bin/env bash
#
# Set up Ansible on a Vagrant Ubuntu trusty box, then run the
# development playbook.

echo "provisioning...."

if [[ ! $(ansible --version 2> /dev/null) =~ 1\.6 ]]; then
	sudo apt-get update && \
	sudo apt-get -y install python-software-properties && \
	sudo apt-get -y install software-properties-common && \
	sudo apt-get -y install gcc build-essential libssl-dev libffi-dev python-dev && \
	sudo apt-get -y install python-pip && \
	sudo pip install -U pip && \
	sudo pip install ansible && \
	sudo pip install virtualenv
fi

PYTHONUNBUFFERED=1 ansible-playbook /vagrant/devops/site.yml \
    --inventory-file=/vagrant/devops/inventory/development \
    --connection=local --limit=app_servers
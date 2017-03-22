env=development
process=all
group=all

ANSIBLE = ansible $(group) -i devops/inventory/$(env)
ANSIBLE_PLAYBOOK = ansible-playbook -i devops/inventory/$(env)

# Match any playbook in the devops directory
% :: devops/%.yml
	$(ANSIBLE_PLAYBOOK) $< -l $(group)

# Match any playbook in the devops directory
% :: devops/%.yml
ifdef tags
	$(ANSIBLE_PLAYBOOK) $< -l $(group) -t $(tags)
else ifdef commit
	$(ANSIBLE_PLAYBOOK) $< -l $(group) -e 'APP_VERSION=$(commit)'
else ifdef limit
	$(ANSIBLE_PLAYBOOK) $< -l $(group) --limit $(limit)
else
	$(ANSIBLE_PLAYBOOK) $< -l $(group)
endif



status :
	$(ANSIBLE) -s -a "supervisorctl status"


restart start stop :
	$(ANSIBLE) -s -a "supervisorctl $(@) $(process)"

restart-supervisor :
	ansible app_servers -i devops/inventory/$(env) -m shell -s \
	-a "service supervisor stop && sleep 5 && service supervisor start"

help:
	@echo ''
	@echo 'Usage: '
	@echo ' make <command> [option=<option_value>]...'
	@echo ''
	@echo 'Setup & Deployment:'
	@echo ' make configure		Prepare servers'
	@echo ' make deploy 		Deploy app'
	@echo ''
	@echo 'Options:  '
	@echo ' env			Inventory file (Default: development)'
	@echo ' group			Inventory subgroup (Default: all)'
	@echo ''
	@echo 'Example:'
	@echo ' make configure env=staging group=app_servers'
	@echo ''
	@echo 'Application Management:'
	@echo ' make status 		Display process states'
	@echo ' make start		Start processes'
	@echo ' make restart		Restart processes'
	@echo ' make restart-supervisor	Restart supervisord'
	@echo ''
	@echo 'Options: '
	@echo ' process		A supervisor program name or group (Default: all)'
	@echo ''
	@echo 'Example:'


shell:
	@python manage.py shell_plus --settings=settings.development


# use sqlite for tests, its faster.
test:
	@python manage.py test wallet --settings=settings.test


run2:
	@sudo killall -9 supervisord &
	@sudo killall -9 gunicorn &
	@python manage.py check --settings=settings.development &
	@python manage.py collectstatic --noinput --settings=settings.development  &
	@python manage.py migrate --settings=settings.development --verbosity 3
	@python manage.py runserver 0.0.0.0:3000 --settings=settings.development

mk:
	@python manage.py makemigrations --settings=settings.development notification_management customer_wallet_management wallet_transactions bill_management

migrate:
	@python manage.py migrate --settings=settings.development

help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  migrations	=> to make model migrations"
	@echo "  clean		=> to clean clean all automatically generated files"
	@echo "  install 	=> to build, uninstall and install package in current pip"

clean:
	find . -name \*.pyc -delete
	find . -name \*__pycache__ -delete

migrations:
	./manage.py makemigrations

install:
	@echo ""
	@echo "\033[32mGenerating tar.gz\033[0m"
	@echo ""
	python setup.py sdist

	@echo ""
	@echo "\033[32mRemoving current installation\033[0m"
	@echo ""
	pip uninstall django-onmydesk -y

	@echo ""
	@echo "\033[32mInstalling new version\033[0m"
	@echo ""
	pip install dist/*.tar.gz

test:
	tox

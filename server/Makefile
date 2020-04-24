VIRTUALENV ?= virtualenv
VRITUALENVARGS =

FILES=server.py

test:
	(echo $(FILES) | entr sh -c 'make test-noentr

test-noentr:
	python -m coverage run -m unittest server && coverage report --omit=p/\* -m -i

env:
	($(VIRTUALENV) $(VIRTUALENVARGS) p && . ./p/bin/activate && pip install -r requirements.txt)



.PHONY: all run clean migrate



all: todomanager-venv run
	echo "hello"


clean:
	rm -rf todoman-venv todoman.egg-info


todomanager-venv:
	python3 -m venv todomanager-venv
	. todomanager-venv/bin/activate && pip install -e .


run: todomanager-venv
	. todomanager-venv/bin/activate && python3 manage.py runserver



migrate: todomanager-venv
	. todomanager-venv/bin/activate && python3 manage.py migrate



makemigrations: todomanager-venv
	. todomanager-venv/bin/activate && python3 manage.py makemigrations


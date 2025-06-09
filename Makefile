

.PHONY: all run clean migrate makemigrations



all: run
	echo "Ran todomanager."


clean:
	rm -rf todomanager-venv todomanager.egg-info vite-project/node_modules db.sqlite3


todomanager-venv:
	python3 -m venv todomanager-venv
	. todomanager-venv/bin/activate && pip install -e .


vite-project/node_modules:
	cd vite-project && npm install


run:
	trap 'kill 0' INT TERM; \
    make rundjango & \
    make runvite & \
	wait


rundjango: todomanager-venv
	. todomanager-venv/bin/activate && python3 manage.py runserver


runvite: vite-project/node_modules
	cd vite-project && npm run build



migrate: todomanager-venv
	. todomanager-venv/bin/activate && python3 manage.py migrate



makemigrations: todomanager-venv
	. todomanager-venv/bin/activate && python3 manage.py makemigrations


test:
	source todomanager-venv/bin/activate && python3 manage.py test todosapp -v 2
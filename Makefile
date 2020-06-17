all: install check run
run:
	python3 main.py
debug:
	POKERBOT_DEBUG=1 python3 main.py
check:
	python3 -m flake8 .
install:
	pip3 install -r requirements.txt
token.txt:
	printf $(TOKEN) > token.txt
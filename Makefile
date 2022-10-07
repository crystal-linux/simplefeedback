test:
	python3 app.py
pip:
	sudo pip3 install -r requirements.txt
deploy: pip
	cp sample.service new.service
	# yes, this exists because I'm too lazy to escape regex + inline 'sed'
	python3 sed.py
	sudo mv new.service /etc/systemd/system/simplefeedback.service
	sudo systemctl daemon-reload
	sudo systemctl enable --now simplefeedback.service
undeploy:
	sudo systemctl stop simplefeedback.service
	sudo systemctl disable simplefeedback.service
	sudo rm /etc/systemd/system/simplefeedback.service
	sudo systemctl daemon-reload
update:
	make undeploy
	git pull
	make deploy

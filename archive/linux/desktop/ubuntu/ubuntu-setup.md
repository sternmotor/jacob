1.0 apt-get install -y vim nmap git 

1.1 Terminal Edit > Profile preferences
	Schriftart: 
	Ubuntu Mono Regular 11

	Colors Monokai
		FG #F8F8F2
		BG #282828
		BOLD #F8F8F0

	Keyboard > Shortcuts
	Launchers
		Launch Termin Alt-Space
		Launch Browser SUPER-2
		Launch Mail client SUPER-3
	Navigation
		Switch to workspace: CTRL + UDLR
		Move Window: STRG + Super + UDLR
		
	Windows
		Resize: Super + UDLR
	System Lock Screen STRG-ALT-DELETE

TODO: Mail / Browser immer im gleichem Viewport öffnen
		
			

1.2 SSH
	ssh-keygen -C gmann@thinkpad -b 4096

1.3 Netzlaufwerke
	Festplatte > Fenster links unten Connect Server "smb://file.ft.local/Systemhaus"


2. : VMware Windows 10
	* VM ware download benötigt jdownloader unter docker

1. Docker installieren
	apt-get install apt-transport-https ca-certificates
	apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
	# xenial noch nicht verfügbar > wili installation
	echo 'deb https://apt.dockerproject.org/repo ubuntu-wily main' > /etc/apt/sources.list.d/docker.list
	apt-get update
	apt-get install -y linux-image-extra-$(uname -r) apparmor docker-engine 
	GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"
	update-grub
	sudo systemctl enable docker  #auto-start

	Maintenance: sudo apt-get upgrade docker-engine

	docker als user betreiben
	groupadd docker
	gpasswd -a gmann docker

	run x11 apps in docker: see http://fabiorehm.com/blog/2014/09/11/running-gui-apps-with-docker/
	

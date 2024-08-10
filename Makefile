asar/asar:
	cd vendor/asar && cmake src && make asar-standalone
	cp vendor/asar/asar/bin/* asar/
clean:
	cd vendor/asar && cmake src && make clean
	rm -f asar/asar
	rm -f asar/asar.exe
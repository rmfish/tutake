.PHONY : run

run : package clean

package :
	python setup.py bdist_wheel

clean :
	rm -rf build
	rm -rf tutake.egg-info
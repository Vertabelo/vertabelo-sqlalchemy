#! /bin/bash


function cleanup() {
	rm -f example_model*.py
}


cleanup

for python in python2 python3
do
	for version in v2.2 v2.3
	do
		model=example_${version}.xml
		out=example_model_${python}_${version}.py
		$python ../vertabelo_sqlalchemy.py -i $model -o $out
	done
done


res=`sha1sum  *.py | awk '{print $1;}'  | sort | uniq -c | awk '{print $1}' | tr -d "\n"`

if [ ! $res -eq "4" ]
then
	echo "Tests failed."
	echo "All files must have the same content"
	sha1sum *.py
	exit 1
else 
	echo "OK"
	cleanup
fi

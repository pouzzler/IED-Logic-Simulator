# Makefile for IED Logic Simulator (c) Sébastien MAGNIEN & Mathieu FOURCROY 2014
all:
	cd help;	\
	qhelpgenerator doc.qhp -o doc.qch;	\
	qcollectiongenerator collection.qhcp -o collection.qhc
	git add src/gui/*.py src/engine/*.py lang icons Makefile help
	git commit -m "$(msg)"
	git push

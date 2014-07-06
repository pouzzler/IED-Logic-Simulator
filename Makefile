# Makefile for IED Logic Simulator (c) Sébastien MAGNIEN & Mathieu FOURCROY 2014
all:
	cd help;	\
	qhelpgenerator doc.qhp -o doc.qch;	\
	qcollectiongenerator collection.qhcp -o collection.qhc
	mv help/collection.qhc .
	mv help/doc.qch .

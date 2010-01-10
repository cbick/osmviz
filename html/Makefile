doc::
	env PYTHONPATH=$(PYTHONPATH):../src/ pydoc -w osmtools.manager
	env PYTHONPATH=$(PYTHONPATH):../src/ pydoc -w osmtools.animation
	env PYTHONPATH=$(PYTHONPATH):../src/ pydoc -w osmtools

examples::
	python py2html.py ../examples/multiple_trackvizs.py > multiple_trackvizs.py.html
	python py2html.py ../examples/pil_example.py > pil_example.py.html
	python py2html.py ../examples/custom_animations.py > custom_animations.py.html


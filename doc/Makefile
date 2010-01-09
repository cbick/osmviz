doc::
	env PYTHONPATH=$(PYTHONPATH):../src/ pydoc -w osmtools.manager
	env PYTHONPATH=$(PYTHONPATH):../src/ pydoc -w osmtools.animation
	env PYTHONPATH=$(PYTHONPATH):../src/ pydoc -w osmtools

examples::
	python ../html/py2html.py ../examples/multiple_trackvizs.py > multiple_trackvizs.py.html
	python ../html/py2html.py ../examples/pil_example.py > pil_example.py.html
	python ../html/py2html.py ../examples/custom_animations.py > custom_animations.py.html


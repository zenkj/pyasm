all: mandelbrot.as

brainfuck.py: brainfuck.pas
	python pyasm.py $< >$@

mandelbrot.as: mandelbrot.bf brainfuck.py
	python brainfuck.py $< >$@

clean:
	rm -f brainfuck.py mandelbrot.as

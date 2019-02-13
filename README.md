# midi_query
Software with different approaches to recognize the song by a shorter querry in midi-format

# Dataset:
https://github.com/jukedeck/nottingham-dataset

# Search algorithms implemented:
Smith-Waterman Search after https://doi.org/10.1016/0022-2836(81)90087-5

DTW using https://librosa.github.io/librosa/generated/librosa.core.dtw.html

Symbolic Fingerprinting after Arzt et al. (http://www.cp.jku.at/research/papers/Arzt_etal_ISMIR_2012.pdf and http://www.cp.jku.at/research/papers/Arzt_etal_ISMIR_2014.pdf)

# Used external files:
https://github.com/rhetr/seq-gui for basis of the GUI

https://github.com/snowwlex/QtWaitingSpinner as beautiful waiting animation

# Libraries:
* python-midi https://github.com/vishnubob/python-midi

* numpy http://www.numpy.org/

* madmom https://github.com/CPJKU/madmom

* scipy https://www.scipy.org/

* cython https://cython.org/

* mido https://github.com/olemb/mido

* pytest https://www.pytest.org/

* pyfftw https://github.com/pyFFTW/pyFFTW

* pyaudio http://people.csail.mit.edu/hubert/pyaudio/

* PyQt5 https://www.riverbankcomputing.com/software/pyqt/intro

* ffmpeg -python https://github.com/kkroening/ffmpeg-python

* FFmpeghttps://www.ffmpeg.org/

* Pygame https://www.pygame.org/news

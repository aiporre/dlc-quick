# dlc-quick
Installation:

- Install anaconda:
https://www.anaconda.com/distribution/
- Install CUDA drivers for your OS 
- Create conda environment:
```
 $ conda create quick-dlc 
```
- Install conda environment for your OS:
```
$ # macOS CPU
$ conda env update --file conda-environments/dlc-macOS-CPU.yaml
$ # Ubuntu GPU
$ conda env update --file conda-environments/dlc-ubuntu-GPU.yaml
$ # Windows CPU
$ conda env update --file conda-environments/dlc-windowsCPU.yaml
$ # Windows GPU
$ conda env update --file conda-environments/dlc-windowsGPU.yaml
``` 

## Test

To quickly look if the instalation was succesful run the test script provided
by the DeepLabCut group with:
```python
$ pythonw test.py # in macOs
$ python test.py # in windows and linux
```
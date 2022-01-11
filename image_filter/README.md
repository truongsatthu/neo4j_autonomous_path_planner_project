# image_filter
## Dependencies
python3 <br/>
opencv-python
## usage
require either `--append_dst` or `--normal_dst`.
`--append_dst` is folder path.
`--normal_dst` is folder path and file name.
### 1. Erosion
```shell
$ python3 Erosion.py 'source_path' kernel (--append_dst|--normal_dst) [--OPTIONS]
```
#### option: ###
+ --kernelX <int>
+ --kernelY <int>

### 2. Dilation
```shell
$ python3 Dilation.py 'source_path' kernel (--append_dst|--normal_dst) [--OPTIONS]
```
#### option: ###
+ --kernelX <int>
+ --kernelY <int>

## Tips ##
### Filter and Parameters append name ###
using `--append_dst` , the value behavior like prefix. and script append there filter name and parameters after source file name.
```shell
$ python3 Erosion.py './img/test.png' 3 --append_dst './img/'
~/img/test-E(3,3).png
```
### Pipe line with standard I/O
using `--cmd`, script standard output becomes only output file name. So you can use pipe line.
```shell
$ python3 Erosion.py './img/test.png' 3 --append_dst './img/' --cmd | ./Dilation.py 3 --append_dst './img/' --cmd 
~/img/test-E(3,3)-D(3,3).png
``` 
### Ex: ###
```shell
$ python3 Dilation.py './img/test.png' 5 --append_dst './img/' --kernelX 1 --kernelY 2 --cmd 
$ python3 Erosion.py './img/test-D(1,2).png' 5 --append_dst './img/' --kernelX 3 --kernelY 3 --cmd 
$ python3 Fillwall.py './img/test-D(1,2)-E(3,3).png' './img/test-D(1,2)-E(3,3)-fillwalled.png'
```
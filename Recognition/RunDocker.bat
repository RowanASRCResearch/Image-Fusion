docker-machine ls
docker-machine start cdocker
docker-machine env --shell cmd cdocker >nul
@FOR /f "tokens=*" %%i IN ('docker-machine env --shell cmd cdocker') DO @%%i>nul
set dock>nul
docker images
REM Must be hard coded paths, modify offline for one's self.
set classify=/src/Libraries/tensorflow-0.6.0/tensorflow/models/image/imagenet/classify_image.py
set mnt="/c/Users/bill/Documents/Code Repositiories/Image-Fusion/:/src"

docker run -p 8888:8888 -p 6006:6006 -v %mnt% -it 7e0be98eae06 python %classify% --image_file %1
REM docker run -p 8888:8888 -p 6006:6006 -v %mnt% -it 32cde1dd0251 bash
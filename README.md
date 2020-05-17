```sh
curl http://download.tensorflow.org/example_images/flower_photos.tgz | tar xz -C . && mv flower_photos training_photos_sample

docker build -t ml-test .

docker run -u `id -u` -p 6006:6006 -it -v "$PWD:/data" ml-test /ai/main.py --train --steps=100
```
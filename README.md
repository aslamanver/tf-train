```sh
curl http://download.tensorflow.org/example_images/flower_photos.tgz | tar xz -C . && mv flower_photos training_photos_sample

docker build -t tf-train:latest .

docker tag tf-train:latest aslamanver/tf-train:latest

docker run -it -p 6006:6006  -v "$PWD:/data" -u "$(id -u):$(id -g)" aslamanver/tf-train /ai/main.py --train
```
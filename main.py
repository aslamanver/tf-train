#!/usr/bin/env python

import sys
import os
import argparse
import glob

os.system("")


class Colors():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def print_color(color, text):
    print(color + text + Colors.RESET)


def main():

    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("--train", help="Action [action = train]", required=True, action="store_true")
    optional.add_argument("--tensorboard", help="Open TensorBoard", action="store_true")
    optional.add_argument("--steps", help="Training steps | Default: 500", default="500", type=int)
    optional.add_argument("--download", help="Model Download | Default: False", action="store_true")
    optional.add_argument("--arch", help="Architecture | Default: mobilenet_1.0_224", default="mobilenet_1.0_224", type=str)
    optional.add_argument("--size", help="Image Size | Default: 224", default=224, type=int)
    optional.add_argument("--convert", help="TF-Lite Convert [FLOAT, QUANT]", type=str)

    args = parser.parse_args()

    retrain_script = "python -m scripts.retrain \
      --bottleneck_dir=/data/bottlenecks \
      --how_many_training_steps=" + str(args.steps) + " \
      --model_dir=/data/models/ \
      --summaries_dir=/data/training_summaries/" + args.arch + " \
      --output_graph=/data/results/model.pb \
      --output_labels=/data/results/labels.txt \
      --architecture=" + args.arch + " \
      --image_dir=/data/training_photos"

    tflite_float_script = "toco \
    --input_format=TENSORFLOW_GRAPHDEF \
    --input_file=/data/results/model.pb \
    --output_format=TFLITE \
    --output_file=/data/results/float_model.tflite \
    --inference_type=FLOAT \
    --inference_input_type=FLOAT \
    --input_arrays=input \
    --output_arrays=final_result \
    --input_shapes=1," + str(args.size) + "," + str(args.size) + ",3 \
    --mean_values=128 \
    --std_values=128 \
    --default_ranges_min=0 \
    --default_ranges_max=6"

    tflite_quant_script = "toco \
    --input_format=TENSORFLOW_GRAPHDEF \
    --input_file=/data/results/model.pb \
    --output_format=TFLITE \
    --output_file=/data/results/quant_model.tflite \
    --inference_type=QUANTIZED_UINT8 \
    --inference_input_type=QUANTIZED_UINT8 \
    --input_arrays=input \
    --output_arrays=final_result \
    --input_shapes=1," + str(args.size) + "," + str(args.size) + ",3 \
    --mean_values=128 \
    --std_values=128 \
    --default_ranges_min=0 \
    --default_ranges_max=6"

    test_script = lambda file: "python -m scripts.label_image \
        --graph=/data/results/model.pb \
        --image=" + file

    if args.tensorboard:
        try:
            os.system("pkill -f tensorboard")
            print_color(Colors.YELLOW, "Tensorboard is running at http://localhost:6006")
            os.system("tensorboard --logdir /data/training_summaries")
        except KeyboardInterrupt:
            pass
        return

    if args.convert:
        if args.convert == "FLOAT":
            print_color(Colors.YELLOW, "Converting to FLOAT model...")
            os.system(tflite_float_script)
        elif args.convert == "QUANT":
            print_color(Colors.MAGENTA, "Converting to QUANTIZED_UINT8 model...")
            os.system(tflite_quant_script)
        else:
            print_color(Colors.RED, "Type is not supported.")
        return

    print_color(Colors.BLUE, "Step 1/5 : Preparing training data...")
    if not os.path.exists("/data/training_photos"):
        print_color(Colors.RED, "training_photos folder is not accessible.")
        sys.exit()

    print("Creating results folder...")
    os.system("mkdir -p /data/results")
    os.system("rm -r /data/results/*")

    if args.download:
        print("Downloading model files from Google...")
        os.system("rm -r /data/models")
    else:
        print("Copying model files from ai...")
        os.system("mkdir -p /data/models")
        os.system("cp -r /ai/models/* /data/models")

    print_color(Colors.BLUE, "Step 2/5 : Starting TensorBoard...")
    os.system("pkill -f tensorboard")
    os.system("tensorboard --logdir /data/training_summaries &")

    print_color(Colors.BLUE, "Step 3/5 : Training model...")
    os.system(retrain_script)

    if not os.path.exists("/data/results/model.pb"):
        print_color(Colors.RED, "results/model.pb file is not accessible.")
        sys.exit()

    print_color(Colors.BLUE, "Step 4/5 : Testing model...")
    for file in glob.glob("/data/testing_photos/*.jpg"):
        print_color(Colors.YELLOW, "\nPredicting... --> " + file)
        os.system(test_script(file))

    print_color(Colors.BLUE, "Step 5/5 : Converting TensorFlow-Lite model...")
    print_color(Colors.MAGENTA, "Converting to FLOAT model...")
    os.system(tflite_float_script)

    print_color(Colors.MAGENTA, "Converting to QUANTIZED_UINT8 model...")
    os.system(tflite_quant_script)

    try:
        print_color(Colors.GREEN, "The training is successful --> results/model.pb.")
        print_color(Colors.BLUE, "Tensorboard is running at http://localhost:6006.")
        input(Colors.BLUE + "Press any key to exit... ")
    except KeyboardInterrupt:
        print("\nContainer is exiting...")


if __name__ == "__main__":
    main()

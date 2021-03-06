import json
import os
import argparse

markdown_code = str()

framework_list = ['caffe', 'cntk', 'coreml', 'darknet', 'mxnet', 'pytorch', 'tensorflow']  # Haven't add 'keras' yet
frame_model_map = {
     'caffe': {'architecture':'prototxt', 'weights':'caffemodel'},
     'cntk': {'architecture':'model'},
     'coreml': {'architecture':'mlmodel'},
     'darknet': {'architecture':'cfg', 'weights':'weights'},
     'mxnet': {'architecture':'json', 'weights':'params'},
     'pytorch': {'architecture':'pth'},
     'tensorflow': {'architecture':'tgz'}
}  # Haven't add 'keras' yet
dataset_list = ['imagenet', 'imagenet11k', 'Pascal VOC', 'grocery100']

def add_code(code):
    global markdown_code
    markdown_code += code

def add_header(level, code):
    add_code("#" * level + " " + code + '\n\n')

def draw_line(num):
    add_code("| " * num + "|\n")
    add_code(("|-" * num + "|\n"))

def save_code(filepath):
    with open(filepath, 'w') as f:
        f.write(markdown_code)
    print("Markdown generate succeeded!")

def LoadJson(json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return data

def GenerateModelBlock(model):
    link = model["link"]
    framework = model["framework"]

    # generate makedown script
    add_code('''|<b>{}</b><br />Framework: {}<br />Dataset: _{}_ <br />Download: '''.format(
        model["name"],
        model["framework"],
        model["dataset"],
    ))
    for k in link.keys():
        if link[k]:
            add_code("[{}]({}) ".format(frame_model_map[framework][k], link[k]))
    add_code("<br />Source: ")
    if (model["source"]!=""):
        add_code("[Link]({})".format(model["source"]))
    add_code("<br />")

def GenerateModelsList(data):
    colnum = 3
    add_header(1, "Model Collection")
    draw_line(colnum)
    models = data["models"]
    num = 0
    for i in range(len(data["models"])):
        if ((models[i]["framework"]!="keras") and (models[i]["link"]["architecture"]!="")):
            GenerateModelBlock(models[i])
            num += 1
            if num % colnum == 0:
                add_code("\n")
    add_code("\n")

def GenerateIntroductionAndTutorial():
    # MMdnn introduction
    add_header(1, "Introduction")
    text_intro='''This is a collection of pre-trained models in different deep learning frameworks.\n
You can download the model you want by simply click the download link.\n
With the download model, you can convert them to different frameworks.\n
Next session show an example to show you how to convert pre-trained model between frameworks.\n\n'''
    add_code(text_intro)

    # steps for model conversion
    add_header(2, "Steps to Convert Model")
    text_example='''**Example: Convert vgg19 model from Tensorflow to CNTK**\n
1. Install the stable version of MMdnn
    ```bash
    pip install mmdnn
    ```
2. Download Tensorflow pre-trained model
    - [x] **Method 1:** Directly download from below model collection
    - [x] **Method 2:** Use command line
    ```bash
        $ mmdownload -f tensorflow -n vgg19

        Downloading file [./vgg_19_2016_08_28.tar.gz] from [http://download.tensorflow.org/models/vgg_19_2016_08_28.tar.gz]
        progress: 520592.0 KB downloaded, 100%
        Model saved in file: ./imagenet_vgg19.ckpt
    ```
    **NOTICE:** _the model name after the **'-n'** argument must be the models appearence in the below model collection._

3. Convert model architecture(*.ckpt.meta) and weights(.ckpt) from Tensorflow to IR
    ```bash
    $ mmtoir -f tensorflow -d vgg19 -n imagenet_vgg19.ckpt.meta -w imagenet_vgg19.ckpt  --dstNodeName MMdnn_Output

    Parse file [imagenet_vgg19.ckpt.meta] with binary format successfully.
    Tensorflow model file [imagenet_vgg19.ckpt.meta] loaded successfully.
    Tensorflow checkpoint file [imagenet_vgg19.ckpt] loaded successfully. [38] variables loaded.
    IR network structure is saved as [vgg19.json].
    IR network structure is saved as [vgg19.pb].
    IR weights are saved as [vgg19.npy].
    ```
4. Convert models from IR to PyTorch code snippet and weights
    ```bash
    $ mmtocode -f pytorch -n vgg19.pb --IRWeightPath vgg19.npy --dstModelPath pytorch_vgg19.py -dw pytorch_vgg19.npy

    Parse file [vgg19.pb] with binary format successfully.
    Target network code snippet is saved as [pytorch_vgg19.py].
    Target weights are saved as [pytorch_vgg19.npy].
    ```
5. Generate PyTorch model from code snippet file and weight file
    ```bash
    $ mmtomodel -f pytorch -in pytorch_vgg19.py -iw pytorch_vgg19.npy --o pytorch_vgg19.pth

    PyTorch model file is saved as [pytorch_vgg19.pth], generated by [pytorch_vgg19.py] and [pytorch_vgg19.npy].
    Notice that you may need [pytorch_vgg19.py] to load the model back.
    ```
'''
    add_code(text_example)
    add_code("\n\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, default="modelmap2.json", help="the path of json file")
    parser.add_argument('-d', '--distFile', type=str, default="README.md", help="the path of the readme file")
    args = parser.parse_args()

    # Generate model converter description
    GenerateIntroductionAndTutorial()

    # Generate models list
    data = LoadJson(args.file)
    GenerateModelsList(data)
    save_code(args.distFile)

if __name__ == "__main__":
    main()
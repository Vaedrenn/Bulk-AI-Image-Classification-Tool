# Bulk AI Image Classification Tool

An image tagger based on deepdanbooru AI

![](img.png)

## Installation and Running
### Prerequisites
+ Python 3.9 - 3.11
+ Windows 10/11
+ 3GB+ of RAM
### Installation on Windows 10/11 using release package
https://github.com/Vaedrenn/Bulk-AI-Image-Classification-Tool/releases

### Building from source
Assuming you've already set up the virtual environment
```bash
pip install -r requirements.txt
pip install .
python main.py
```
- As of 02/28/2024 tensorflow-io does not have a working package for python 3.12
- Tensorflow no longer support GPUs on Windows as of Version 2.10
## Models
Models are not included, must be downloaded seperately. Currently only supports deepdanbooru

### DeepDanbooru
Anime style image classification model based on the Gwern 2021 dataset. Best used for tagging digital drawings but also preforms well enough other mediums.

Download: https://github.com/KichangKim/DeepDanbooru/releases

### Custom Models
For the time being models should be in the following format:
```
/Bulk-AI-Image-Classification-Tool/
└── /models/
    └── /model_name/
        ├── model-resnet_custom_v3.h5 (required)
        └── tags.txt (required)
        └── tags-character.txt (optional)
```
- Models and tags are loaded via action_box's load_model and load_tags function, which look for the above files respectively
## Usage
### Generating Tags
1. Load model using the browse button located at next to the input that says model.
2. Specify folder path, does not tag subdirectories.
3. Specify threshold limits. Tags are based on probability of correctness, if probability is greater than threshold then that tag is added to results. This is based on the model provided.
4. Click Submit to generate tags for all images.

### Editing Tags
#### Adding tags
- Don't see a tag in results? Type it in the add tag box and hit enter.
#### Removing Tags
- Uncheck the tag you don't want and then click 'Save Changes'


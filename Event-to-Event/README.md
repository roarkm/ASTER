# Event To Event
Trains model and predicts events?

## Usage
**Install & Setup**
`virtualenv -p python2.7 .venv && source .venv/bin/activate && pip install -r requirements.txt`

Note: Currently using tensorflow 1.3.
Once this is working with tf1.3, will also try with latest tensorflow-gpu 1.13.1
(my RTX-2070 is only compatible with CUDA-10 and only tensorflow-gpu v1.13+ supports CUDA-10).

**Event-to-Event**
code relies on Tensorflow 1.3,
edit hyperparameters in **cmu_translate.py** and run using python 2.7 to train the model
and use **cmu_translate_decode.py** to decode.

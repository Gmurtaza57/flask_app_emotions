# -*- coding: utf-8 -*-
"""Copy of Untitled49.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UGrTxH08bz6RarSWIxWK4iMGMfCe_A5f
"""

!pwd

!pip install livelossplot==0.5.2

!pip install keras

!pip install utils

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import utils
import os
# %matplotlib inline

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Input, Dropout,Flatten, Conv2D
from tensorflow.keras.layers import BatchNormalization, Activation, MaxPooling2D
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import plot_model

from IPython.display import SVG, Image
from livelossplot import PlotLossesKeras
#from livelossplot import PlotLossesTensorFlowKeras
import tensorflow as tf
print("Tensorflow version:", tf.__version__)

import zipfile
with zipfile.ZipFile("dataset.zip", 'r') as zip_ref:
    zip_ref.extractall()

for expression in os.listdir("images/train/"):
    print(str(len(os.listdir("images/train/"+expression)))+ " "+ expression + " images")

start = "\033[1m"
end = "\033[0;0m"
list1=["angry","disgust","fear","happy","neutral","sad","surprise"]
list2=["/10002","/10018","/10072","/10001","/10054","/10255","/660"]
import cv2 as cv
sum=0
for folder in list1:
    img2=cv.imread("images/train/"+folder+list2[sum]+".jpg",0)
    print(start+"************************{}*************************".format(folder)+end)
    plt.imshow(img2)
    plt.show()
    sum+=1

img_size  = 48
batch_size = 64

datagen_train = ImageDataGenerator(horizontal_flip=True)
train_generator = datagen_train.flow_from_directory("images/train",
                                                    target_size=(img_size, img_size),
                                                    color_mode='grayscale',
                                                    batch_size=batch_size,
                                                    class_mode='categorical',
                                                    shuffle=True)

datagen_validation = ImageDataGenerator(horizontal_flip=True)
validation_generator = datagen_validation.flow_from_directory("images/validation",
                                                    target_size=(img_size, img_size),
                                                    color_mode='grayscale',
                                                    batch_size=batch_size,
                                                    class_mode='categorical',
                                                    shuffle=True)
for expression in os.listdir("images/train/"):
    print(str(len(os.listdir("images/train/"+expression)))+ " "+ expression + " images")

model = Sequential()

#1 - conv
model.add(Conv2D(64, (3,3), padding = 'same', input_shape=(48,48,1)), )
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.20))

#2 - conv layer
model.add(Conv2D(128, (5,5), padding = 'same'))
model.add(BatchNormalization())
model.add(Activation('elu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.20))


# 3- conv layer
model.add(Conv2D(512, (3,3), padding = 'same'))
model.add(BatchNormalization())
model.add(Activation('elu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.20))


# 4 - conv layer
model.add(Conv2D(512, (3,3), padding = 'same'))
model.add(BatchNormalization())
model.add(Activation('elu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.20))

model.add(Flatten())

model.add(Dense(256))
model.add(BatchNormalization())
model.add(Activation('elu'))
model.add(Dropout(0.25))

model.add(Dense(512))
model.add(BatchNormalization())
model.add(Activation('elu'))
model.add(Dropout(0.25))


model.add(Dense(7,activation='softmax'))
opt = Adam(lr=0.0005)
model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()
plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

epochs = 200

checkpoint = ModelCheckpoint("model_weights.h5", monitor = 'val_acccuracy',
                            save_weigths_only=True, mode='max', verbose=1)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor = 0.01, patience =2, min_lr=0.00001, model = 'auto')

#callbacks = [PlotLossesCallback(), checkpoint, recduce_lr]
callbacks = [PlotLossesKeras(), checkpoint, reduce_lr]
history = model.fit(
    x=train_generator,
    epochs=epochs,
    validation_data=validation_generator,
    callbacks=callbacks
)

#only selecting the convolution layers for showing activation maps
conv_layers = [1, 6, 11]
outputs = [model.layers[i].output for i in conv_layers]

conv_model1 = Model(inputs=model.inputs, outputs=outputs)
# load the image with the required shape
# expanding dimensions to make it array of [0,0,0,0] dimensions
img = np.expand_dims(img2, axis=0)

feature_maps = conv_model1.predict(img)
# plotting in size of 16x16 for every convolution layer
box = 24

for f_map in feature_maps:
  plt.figure(figsize=(25,25)) 
  print("\n\n \033[1m convolution layer with filter size {} \033[1m \033[0m".format(len(f_map[0,0,0,:])))
  for filter_size in range(len(f_map[0,0,0,:])):
    
    for _ in range(box):
      for _ in range(box):

        plot1 = plt.subplot(box, box, filter_size+1)
        plot1.set_xticks([])
        plot1.set_yticks([])

        plt.imshow(f_map[0, :, :, filter_size-1],cmap="gray")
# show the figure
  plt.show()

model_json = model.to_json()
with open ("model.json", "w") as json_file:
    json_file.write(model_json)

model.fit_generator(train_generator,
                    steps_per_epoch=28821 // batch_size,
                    epochs=1,
                    validation_data=validation_generator,
                    validation_steps=7066 // batch_size)

from sklearn.metrics import classification_report, confusion_matrix
Y_pred = model.predict_generator(validation_generator)
y_pred = np.argmax(Y_pred, axis=1)
print('Confusion Matrix')
print(confusion_matrix(validation_generator.classes, y_pred))
print('Classification Report')
target_names = list(validation_generator.class_indices.keys())
print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

class_names = train_generator.class_indices.keys()

def plot_heatmap(y_true, y_pred, class_names, ax, title):
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(
        cm, 
        annot=True, 
        square=True, 
        xticklabels=class_names, 
        yticklabels=class_names,
        fmt='d', 
        cmap=plt.cm.Blues,
        cbar=False,
        ax=ax
    )
    ax.set_title(title, fontsize=16)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_xlabel('Predicted Label', fontsize=12)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 10))

plot_heatmap(validation_generator.classes, y_pred, class_names, ax1, title="Base CNN model")
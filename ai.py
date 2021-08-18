from constants import constants
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
from PIL import Image

import numpy as np
import tensorflow as tf

import io

c = constants()

class Oracle:
    def __init__(self, user_id, device_id, data_source):
        self.training_data = [(np.array(Image.open(io.BytesIO(entry[c.EVENT_PICTURE_KEY]))), entry[c.EVENT_PET_KEY])
            for entry in data_source.client.events.find({
                c.DEVICE_ID_KEY: device_id,
                c.USER_EMAIL_KEY: user_id,
            }, {
                c.EVENT_PICTURE_KEY: 1,
                c.EVENT_PET_KEY: 1,
                "_id": 0
            })]

        self.unique = tf.unique([data[1] for data in self.training_data])

        self.model = Sequential()
        self.model.add(Conv2D(32, (3, 3), input_shape=self.training_data[0][0].shape))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))

        self.model.add(Conv2D(32, (3, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))

        # self.model.add(Conv2D(64, (3, 3)))
        # self.model.add(Activation('relu'))
        # self.model.add(MaxPooling2D(pool_size=(2, 2)))

        self.model.add(Flatten())
        self.model.add(Dense(64))
        self.model.add(Activation('relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1)) # <- n should be amount of pets found + 1 (unknown/None)
        self.model.add(Activation('sigmoid'))

        self.model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

        self._fit_history = self.model.fit(x=np.array([data[0] for data in self.training_data]), y=self.unique.idx.numpy(), epochs=5)

    def predict(self, picture):
        guess = self.model.predict(np.array([np.array(Image.open(io.BytesIO(picture)))]))[0][0]
        _guess = int(guess)
        if (guess - int(guess) > .5):
            _guess += 1
        return self.unique.y.numpy()[_guess].decode("UTF-8")
    #     _guess = 0 if guess < .5 else 1
    # print("Guess was {} -> {} ({}% certain) = {}".format(guess, _guess, abs(guess-.5)*100./.5, unique.y.numpy()[_guess]))
    # print("Data was {} ({})".format(pet, "SUCCESS" if unique.y.numpy()[_guess] == bytes(pet, "UTF-8") else "*** FAIL ***"))
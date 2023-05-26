'''
this is the NN for beamforming
input contains three factors maybe ( angle, distance, velocity)
think we need to add the velocity(not sure estimated or the real) as the input

the question remains is if we need to use real_angle and real_distance or the estimated one


2. need to consider the specific output should link to the specific input, to let every user has
linked element of matrix
'''


import tensorflow.keras as keras
from keras.layers import Dense
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
import tensorflow as tf

import config_parameter
from config_parameter import rf_size, antenna_size
class DL_method_NN_with_theta(keras.Model):
    def __init__(self):
        super().__init__()
        act_func = "relu"
        init = keras.initializers.GlorotNormal() #Xavier initializer
        self.conv_layer1 = Conv2D(32, kernel_size=3, activation=act_func, input_shape=(1, 10, 5, 2), kernel_initializer=init, padding="same")
        self.bn1 = keras.layers.BatchNormalization()
        self.maxpool1 = MaxPooling2D()
        self.conv_layer2 = Conv2D(64, kernel_size=3, activation=act_func, kernel_initializer=init, padding="same")
        self.bn2 = keras.layers.BatchNormalization()
        self.maxpool2 = MaxPooling2D()
        self.conv_layer3 = Conv2D(64, kernel_size=3, activation=act_func, kernel_initializer=init, padding="same")
        self.bn3 = keras.layers.BatchNormalization()
        self.maxpool3 = MaxPooling2D()
        self.flatten = Flatten()
        self.dense_1 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_2 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_3 = Dense(600, activation=act_func, kernel_initializer=init)
        self.dense_4 = Dense(600, activation=act_func, kernel_initializer=init)
        #self.dense_5 = Dense(20, activation=act_func, kernel_initializer=init)
        #self.dense_6 = Dense(20, activation=act_func, kernel_initializer=init)
        parameter_size = config_parameter.rf_size*config_parameter.antenna_size + 2*config_parameter.rf_size*config_parameter.num_vehicle +\
                         config_parameter.num_vehicle# the last item is the theta prediction
        self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)


    def call(self, input):
        out = self.conv_layer1(input)
        out = self.maxpool1(out)
        out = self.bn1(out)
        out = self.conv_layer2(out)
        out = self.maxpool2(out)
        out = self.bn2(out)
        #out = self.conv_layer3(out)
        #out = self.maxpool3(out)
        #out = self.bn3(out)
        out = self.flatten(out)

        out = self.dense_1(out)
        out = self.dense_2(out)
        out = self.dense_3(out)
        out = self.out(out)
        Parameter = tf.clip_by_value(out,1e-10,1-1e-10)


        return Parameter

class DL_method_NN(keras.Model):
    def __init__(self):
        super().__init__()
        act_func = "relu"
        init = keras.initializers.GlorotNormal() #Xavier initializer
        self.conv_layer1 = Conv2D(32, kernel_size=3, activation=act_func, input_shape=(1, 10, 5, 3), kernel_initializer=init, padding="same")
        self.bn1 = keras.layers.BatchNormalization()
        self.maxpool1 = MaxPooling2D()
        self.conv_layer2 = Conv2D(64, kernel_size=3, activation=act_func, kernel_initializer=init, padding="same")
        self.bn2 = keras.layers.BatchNormalization()
        self.maxpool2 = MaxPooling2D()
        self.conv_layer3 = Conv2D(64, kernel_size=3, activation=act_func, kernel_initializer=init, padding="same")
        self.bn3 = keras.layers.BatchNormalization()
        self.maxpool3 = MaxPooling2D()
        self.flatten = Flatten()
        self.dense_1 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_2 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_3 = Dense(600, activation=act_func, kernel_initializer=init)
        self.dense_4 = Dense(600, activation=act_func, kernel_initializer=init)
        #self.dense_5 = Dense(20, activation=act_func, kernel_initializer=init)
        #self.dense_6 = Dense(20, activation=act_func, kernel_initializer=init)
        parameter_size = config_parameter.rf_size*config_parameter.antenna_size + 2*config_parameter.rf_size*config_parameter.num_vehicle
        self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)


    def call(self, input):
        out = self.conv_layer1(input)
        out = self.maxpool1(out)
        out = self.bn1(out)
        out = self.conv_layer2(out)
        out = self.maxpool2(out)
        out = self.bn2(out)
        #out = self.conv_layer3(out)
        #out = self.maxpool3(out)
        #out = self.bn3(out)
        out = self.flatten(out)

        out = self.dense_1(out)
        out = self.dense_2(out)
        out = self.dense_3(out)
        out = self.out(out)
        Parameter = tf.clip_by_value(out,1e-10,1-1e-10)


        return Parameter
class DL_method_NN_Digital(keras.Model):
    def __init__(self):
        super().__init__()
        act_func = "relu"
        init = keras.initializers.GlorotNormal() #Xavier initializer
        self.conv_layer1 = Conv2D(32, kernel_size=3, activation=act_func, input_shape=(1, 10, 5, 2), kernel_initializer=init, padding="same")
        self.bn1 = keras.layers.BatchNormalization()
        self.maxpool1 = MaxPooling2D()
        self.conv_layer2 = Conv2D(64, kernel_size=3, activation=act_func, kernel_initializer=init, padding="same")
        self.bn2 = keras.layers.BatchNormalization()
        self.maxpool2 = MaxPooling2D()
        self.conv_layer3 = Conv2D(64, kernel_size=3, activation=act_func, kernel_initializer=init, padding="same")
        self.bn3 = keras.layers.BatchNormalization()
        self.maxpool3 = MaxPooling2D()
        self.flatten = Flatten()
        self.dense_1 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_2 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_3 = Dense(600, activation=act_func, kernel_initializer=init)
        self.dense_4 = Dense(600, activation=act_func, kernel_initializer=init)
        #self.dense_5 = Dense(20, activation=act_func, kernel_initializer=init)
        #self.dense_6 = Dense(20, activation=act_func, kernel_initializer=init)
        parameter_size = 2*config_parameter.antenna_size*config_parameter.num_vehicle
        self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)


    def call(self, input):
        out = self.conv_layer1(input)
        out = self.maxpool1(out)
        out = self.bn1(out)
        out = self.conv_layer2(out)
        out = self.maxpool2(out)
        out = self.bn2(out)
        #out = self.conv_layer3(out)
        #out = self.maxpool3(out)
        #out = self.bn3(out)
        out = self.flatten(out)

        out = self.dense_1(out)
        out = self.dense_2(out)
        out = self.dense_3(out)
        out = self.out(out)
        Parameter = tf.clip_by_value(out,1e-10,1-1e-10)


        return Parameter
class DL_method_NN_naive_digital(keras.Model):
    def __init__(self):
        super().__init__()
        act_func = "relu"
        init = keras.initializers.GlorotNormal() #Xavier initializer
        self.dense_1 = Dense(1200, activation=act_func,input_shape=(1, 10, 5, 2), kernel_initializer=init)
        self.dense_2 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_3 = Dense(600, activation=act_func, kernel_initializer=init)
        #self.dense_4 = Dense(600, activation=act_func, kernel_initializer=init)
        #self.dense_5 = Dense(20, activation=act_func, kernel_initializer=init)
        #self.dense_6 = Dense(20, activation=act_func, kernel_initializer=init)
        parameter_size = 2*config_parameter.antenna_size*config_parameter.num_vehicle
        self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)


    def call(self, input):


        out = self.dense_1(input)
        out = self.dense_2(out)
        out = self.dense_3(out)
        out = self.out(out)
        Parameter = tf.clip_by_value(out,1e-10,1-1e-10)


        return Parameter


class DL_method_NN_naive_hybrid(keras.Model):
    def __init__(self):
        super().__init__()
        act_func = "relu"
        init = keras.initializers.GlorotNormal()  # Xavier initializer
        self.dense_1 = Dense(1200, activation=act_func, input_shape=(1, 10, config_parameter.num_vehicle, 2), kernel_initializer=init)
        self.dense_2 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_3 = Dense(600, activation=act_func, kernel_initializer=init)
        #self.dense_4 = Dense(600, activation=act_func, kernel_initializer=init)
        # self.dense_5 = Dense(20, activation=act_func, kernel_initializer=init)
        # self.dense_6 = Dense(20, activation=act_func, kernel_initializer=init)
        parameter_size = config_parameter.rf_size * config_parameter.antenna_size + 2 * config_parameter.rf_size * config_parameter.num_vehicle
        self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)

    def call(self, input):
        out = self.dense_1(input)
        out = self.dense_2(out)
        out = self.dense_3(out)
        out = self.out(out)
        Parameter = tf.clip_by_value(out, 1e-10, 1 - 1e-10)

        return Parameter

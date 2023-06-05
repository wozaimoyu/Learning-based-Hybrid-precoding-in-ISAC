'''
this is the NN for beamforming
input contains three factors maybe ( angle, distance, velocity)
think we need to add the velocity(not sure estimated or the real) as the input

the question remains is if we need to use real_angle and real_distance or the estimated one


2. need to consider the specific output should link to the specific input, to let every user has
linked element of matrix

ResNet code snippet partly refers to
MIT License

Copyright (c) 2019 calmisential

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import tensorflow.keras as keras
from keras.layers import Dense,LSTM,Concatenate
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
import tensorflow as tf
import numpy as np
import config_parameter
from tensorflow import keras
from tensorflow.keras.layers import Conv1D, LSTM, Dense, BatchNormalization, Activation, Add,Reshape



from config_parameter import rf_size, antenna_size
def make_bottleneck_layer(filter_num, blocks, stride=1):

    res_block = tf.keras.Sequential()
    #res_block.add(BottleNeck(filter_num, stride=stride))
    #res_block.add(OneD_BottleNeck(filter_num, stride=stride))
    res_block.add(BottleNeck(filter_num, stride=stride))
    for _ in range(1, blocks):
        res_block.add(BottleNeck(filter_num, stride=stride))
        #res_block.add(BottleNeck(filter_num, stride=stride))

        #res_block.add(OneD_BottleNeck(filter_num, stride=stride))
    return res_block


class ResNetLSTMModel(keras.Model):
    def __init__(self):
        super(ResNetLSTMModel, self).__init__()

        act_func = "relu"
        init = keras.initializers.GlorotNormal() #Xavier initializer
        self.conv1 = tf.keras.layers.Conv2D(filters=64,
                                            kernel_size=(7, 7),
                                            strides=2,
                                            padding="same")
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.flatten = Flatten()
        self.dense_1 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_2 = Dense(1200, activation=act_func, kernel_initializer=init)
        self.dense_3 = Dense(600, activation=act_func, kernel_initializer=init)
        self.dense_4 = Dense(600, activation=act_func, kernel_initializer=init)
        num_vehicle = config_parameter.num_uppercar + config_parameter.num_lowercar + config_parameter.num_horizoncar
        parameter_size = config_parameter.rf_size * config_parameter.vehicle_antenna_size + 2 * config_parameter.rf_size * num_vehicle

        self.out = Dense(parameter_size,
                         activation='softmax')  # self.fc = tf.keras.layers.Dense(units=NUM_CLASSES, activation=tf.keras.activations.softmax)
        self.build((1, 10, 3, 32))
    def call(self, inputs):
        #x = self.conv1(inputs)
        #x = self.bn1(inputs)
        out=self.flatten(inputs)
        out = self.dense_1(out)
        out = self.dense_2(out)
        out = self.dense_3(out)
        outputs = self.out(out)
        return outputs


    def build_resnet_block(self, filters, kernel_size):
        resnet_block = keras.Sequential()
        resnet_block.add(Conv2D(filters, kernel_size, padding='same'))
        resnet_block.add(BatchNormalization())
        resnet_block.add(Activation('relu'))
        resnet_block.add(Conv2D(filters, kernel_size, padding='same'))
        resnet_block.add(BatchNormalization())
        resnet_block.add(Add())
        resnet_block.add(Activation('relu'))
        return resnet_block



class DL_method_NN_for_v2x(keras.Model):
    def __init__(self,layer_params=[0,0,0,1]):
        super().__init__()
        self.conv1 = tf.keras.layers.Conv2D(filters=64,
                                            kernel_size=(7, 7),
                                            strides=2,
                                            padding="same")
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.pool1 = tf.keras.layers.MaxPool2D(pool_size=(3, 3),
                                               strides=2,
                                               padding="same")

        self.layer1 = make_bottleneck_layer(filter_num=64,
                                            blocks=layer_params[0])
        self.layer2 = make_bottleneck_layer(filter_num=128,
                                            blocks=layer_params[1],
                                            stride=2)
        self.layer3 = make_bottleneck_layer(filter_num=256,
                                            blocks=layer_params[2],
                                            stride=2)
        self.layer4 = make_bottleneck_layer(filter_num=512,
                                            blocks=layer_params[3],
                                            stride=2)

        self.avgpool = tf.keras.layers.GlobalAveragePooling2D()
        #print(self.avgpool.shape)
        #self.avgpool = tf.reshape(self.avgpool,(1,1,2048))
        self.lstm1= LSTM(64)
        #self.concat =Concatenate()
        # self.fc2 = tf.keras.layers.Dense(units=128, activation=tf.keras.activations.softmax)
        num_vehicle = config_parameter.num_uppercar + config_parameter.num_lowercar + config_parameter.num_horizoncar
        parameter_size = config_parameter.rf_size * config_parameter.vehicle_antenna_size + 2 * config_parameter.rf_size * num_vehicle

        #self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)

        self.out = Dense(parameter_size, activation='softmax')#self.fc = tf.keras.layers.Dense(units=NUM_CLASSES, activation=tf.keras.activations.softmax)


    def call(self, inputs, training=None, mask=None):
        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        x = tf.nn.relu(x)
        x = self.pool1(x)
        feature1 = self.layer1(x, training=training)
        feature2 = self.layer2(feature1, training=training)
        feature3 = self.layer3(feature2, training=training)
        out = self.layer4(feature3, training=training)

        out = self.avgpool(out)
        out = tf.reshape(out,(1,1,2048))
        out =self.lstm1(out)
        #out3 = self.concat
        out = self.out(out)
        # output1= self.fc2(output2)
        # print('PPPPPPPPPPPP',output1.shape) #shape 128x2048

        Parameter = tf.clip_by_value(out,1e-10,1-1e-10)
        # output = output/sum(output)
        return Parameter
class DL_method_NN_for_v2x_mod(keras.Model):
    def __init__(self):
        super().__init__()
        act_func = "relu"
        init = keras.initializers.GlorotNormal() #Xavier initializer
        num_vehicle = config_parameter.num_uppercar + config_parameter.num_lowercar + config_parameter.num_horizoncar
        self.conv_layer1 = Conv2D(32, kernel_size=3, activation=act_func, input_shape=(1, 11, num_vehicle, 3), kernel_initializer=init, padding="same")
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
        num_vehicle = config_parameter.num_uppercar + config_parameter.num_lowercar +config_parameter.num_horizoncar
        parameter_size = config_parameter.rf_size*config_parameter.vehicle_antenna_size + 2*config_parameter.rf_size*num_vehicle

        self.out = Dense(parameter_size, activation='softmax', kernel_initializer=init)


    def call(self, input):
        out = self.conv_layer1(input)
        out = self.maxpool1(out)
        out = self.bn1(out)
        out = self.conv_layer2(out)
        #out = self.maxpool2(out)
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
        #Parameter = tf.clip_by_value(out,1e-10,1-1e-10)
        Parameter = tf.clip_by_value(out, 0.001, 0.999)


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
        #Parameter = tf.clip_by_value(out,1e-10,1-1e-10)
        Parameter = tf.clip_by_value(out, 0.001, 0.999)

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
class BottleNeck(tf.keras.layers.Layer):
    def __init__(self, filter_num, stride=1):
        super(BottleNeck, self).__init__()
        self.conv1 = tf.keras.layers.Conv2D(filters=filter_num,
                                            kernel_size=(1, 1),
                                            strides=1,
                                            padding='same')
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.conv2 = tf.keras.layers.Conv2D(filters=filter_num,
                                            kernel_size=(3, 3),
                                            strides=stride,
                                            padding='same')
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.conv3 = tf.keras.layers.Conv2D(filters=filter_num * 4,
                                            kernel_size=(1, 1),
                                            strides=1,
                                            padding='same')
        self.bn3 = tf.keras.layers.BatchNormalization()

        self.downsample = tf.keras.Sequential()
        self.downsample.add(tf.keras.layers.Conv2D(filters=filter_num * 4,
                                                   kernel_size=(1, 1),
                                                   strides=stride))
        self.downsample.add(tf.keras.layers.BatchNormalization())

    def call(self, inputs, training=None, **kwargs):
        residual = self.downsample(inputs)

        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        x = tf.nn.relu(x)
        x = self.conv2(x)
        x = self.bn2(x, training=training)
        x = tf.nn.relu(x)
        x = self.conv3(x)
        x = self.bn3(x, training=training)

        output = tf.nn.relu(tf.keras.layers.add([residual, x]))

        return output
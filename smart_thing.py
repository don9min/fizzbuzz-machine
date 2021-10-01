#!/usr/bin/python3
# Most of the code is based on https://github.com/joelgrus/fizz-buzz-tensorflow/blob/master/pydata-chicago/deep.py

import socket
import tensorflow.keras as keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
import numpy as np

####### machine learning programming #######
# Fizz Buzz Inference Unit

### global variable setting
flag_realtime_learning = 0      # execute learning process or not
num_digits = 10                 # length of digits to represent the input number in binary
train_start = 101
train_end = 2**(num_digits)
# the number of nodes in the hidden layer
num_hidden1 = 500
num_hidden2 = 500

def ground_truth(i):
    """One-hot encode the desired output: [number, "fizz", "buzz", "fizzbuzz"]"""
    if   i % 15 == 0: return np.array([0, 0, 0, 1])
    elif i % 5  == 0: return np.array([0, 0, 1, 0])
    elif i % 3  == 0: return np.array([0, 1, 0, 0])
    else:             return np.array([1, 0, 0, 0])

def binary_encoder(i, num_digits):
    """Represent each input by an array of its binary digits"""
    return np.array([i >> d & 1 for d in range(num_digits)])

def fizzbuzz_output(i, inference):
    """produce fizzbuzz output"""
    return [str(i), "fizz", "buzz", "fizzbuzz"][inference]


# make training data sequence from the number 101 to (2 ** num_digits - 1)
train_x = np.array([binary_encoder(i, num_digits) for i in range(train_start, train_end)])
train_y = np.array([ground_truth(i) for i in range(train_start, train_end)])

if flag_realtime_learning == 1:

    model = Sequential([
        Dense(num_hidden1, input_dim=10),
        Activation('relu'),
        Dropout(0.5),
        Dense(num_hidden2),
        Activation('relu'),
        Dense(4),
        Activation('softmax')
    ])

    model.compile(optimizer='rmsprop',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    model.fit(train_x, train_y, epochs=200, batch_size=64, shuffle=True)

    model.save("set_fizzbuzz_learning_" + str(train_start) + "_" + str(train_end) + ".h5")
else:
    from tensorflow.keras.models import load_model
    model = load_model('fizzbuzz_learning_101_1024.h5')

#print("train_x:", train_x)
#print("train_y:", train_y)

def inference_unit(numbers):
    """infer right output"""
#    numbers = np.arange(1, 101)
    numbers = np.arange(numbers, numbers+10)
    x = np.transpose(binary_encoder(numbers, num_digits))
#    print("x:",x)
#    inference = [fizzbuzz_output(i+1, y) for i, y in enumerate(np.argmax(model.predict(x), axis=1))]
    inference = [y for i, y in enumerate(np.argmax(model.predict(np.array(x)), axis=1))]
#    print("inference:",inference)
    return inference[0]


def accuracy_test(i):
    """Test accuracy"""
    if   i % 15 == 0: return 3
    elif i % 5  == 0: return 2
    elif i % 3  == 0: return 1
    else:             return 0


####### network programming #######
print("*** START SMART THING ***")

num_iter = 100;
accuracy_cnt = 0;
infer_cnt = 0;
comm_cnt = 0;
raw_x = 1;
raw_y = 0;


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # create a socket object
host = socket.gethostname()                                     # get local machine name
port = 9361                                                    # reserve a port for your service
s.bind(('192.168.0.3', port))                                            # bind to the port
s.listen(5)                                                     # wait for connection
while raw_x <= num_iter:
    # initialize
    c,addr = s.accept()                                         # establish connection with client
    print('Got connection from controller', addr)
    # start fizzbuzz
    val = str(raw_x)
    c.send(val.encode())
    print('Just sent a number', raw_x)
    data = c.recv(65535)
    comm_cnt = comm_cnt + 1
    if int(data) == 1:
        print('Received command:', 'fizz')
    elif int(data) == 2:
        print('Received command:', 'buzz')
    elif int(data) == 3:
        print('Received command:', 'fizzbuzz')
    elif int(data) == 0:
        print('Received command:', raw_x)
    else:
#        call inference procedure
        print('Something wrong, try to guess')
        infered_y = inference_unit(raw_x)
        infer_cnt = infer_cnt + 1
        if infered_y == 1:
            print('Infered command:', 'fizz')
        elif infered_y == 2:
            print('Infered command:', 'buzz')
        elif infered_y == 3:
            print('Infered command:', 'fizzbuzz')
        elif infered_y == 0:
            print('Infered command:', raw_x)
        # measure accuracy
        if infered_y == accuracy_test(raw_x):
            accuracy_cnt = accuracy_cnt + 1
            print("accuracy ratio:", accuracy_cnt, "/", infer_cnt, "=", accuracy_cnt/infer_cnt)
    c.close()                                                   # close the connection

    # state change
    raw_x = raw_x + 1;
    pass

# performance results
print("*** Performance ***")
print("Communication Error Rate:", infer_cnt / comm_cnt);
print("Inference Accuracy Rate:", accuracy_cnt / infer_cnt);

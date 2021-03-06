import tensorflow as tf

"""
this module is just for collecting all models for finding the best one. A tensorflow model should look something like:

def my_model_fn(
   features,  This is batch_features from input_fn
   labels,    This is batch_labels from input_fn
   mode,      An instance of tf.estimator.ModeKeys
   params):   Additional configuration --> dict('feature_columns', 'hidden_layers', 'n_classes')

    every respectable model should contain at least:
    - an input layer
    - some hidden layers (cnn/lstm/whatevur)
    - some dense layer
    - an output layer with a softmax function for proper classification

    MODE ---> they are three in an estimator (train, evaluate, predict) and they need to be taken into account within
    the model.

    for train and evaluate: optimization by minimizing cross entropy (by adam or basic sgd) AND an EstimatorSpec
    instance

    for predict: just an EstimatorSpec instance (in prediction mode we don't expect to optimize furtherly our NN
    
    Let's try to include some Tensorboard code to have some beautiful graphics to display to some cute biologists!

"""


def cnn(features, labels, mode, params):
    x = features['X']

    # 2 cnn layers on ReLU

    # conv2d layers expect 4-dim tensors, reshaping our 3-dim vect

    net = tf.reshape(x, [-1, 1000, 20, 1])

    conv1 = tf.layers.conv2d(inputs=net, filters=30, kernel_size=3,
                             padding="same", activation=tf.nn.relu)

    conv2 = tf.layers.conv2d(inputs=conv1, filters=30, kernel_size=5,
                             padding="same", activation=tf.nn.relu)

    if params['pooling']:

        pool = tf.layers.max_pooling2d(inputs=conv2, pool_size=(2, 2), strides=2)

    else:
        pool = conv2

    pool_flat = tf.layers.flatten(pool)

    dense_1 = tf.layers.dense(inputs=pool_flat, activation=tf.nn.relu, units=1024)

    dropout = tf.layers.dropout(inputs=dense_1, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

    # last layer with no activation function

    logits = tf.layers.dense(dropout, units=params['n_classes'])

    y_pred = tf.nn.softmax(logits=logits)

    y_pred_cls = tf.argmax(y_pred, axis=1)

    if mode == tf.estimator.ModeKeys.PREDICT:

        spec = tf.estimator.EstimatorSpec(mode=mode, predictions=y_pred_cls)

    else:

        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels,
                                                                       logits=logits)

        loss = tf.reduce_mean(cross_entropy)

        optimizer = tf.train.AdamOptimizer(learning_rate=params["learning_rate"])

        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())

        # Define the evaluation metrics,
        # in this case the classification accuracy.
        metrics = \
            {
                "accuracy": tf.metrics.accuracy(labels, y_pred_cls)
            }

        accuracy = tf.contrib.metrics.accuracy(labels, tf.cast(y_pred_cls, tf.int32))

        logging_hooks = tf.train.LoggingTensorHook({'accuracy': accuracy}, every_n_iter=10)

        # Wrap all of this in an EstimatorSpec.
        spec = tf.estimator.EstimatorSpec(
            mode=mode,
            loss=loss,
            train_op=train_op,
            eval_metric_ops=metrics,
            training_chief_hooks=[logging_hooks])

    return spec


def cnn_lstm(features, labels, mode, params):
    x = features['X']

    # 2 cnn layers on ReLU and a forward-backward lstm layer

    # conv2d layers expect 4-dim tensors, reshaping our 3-dim vect

    net = tf.reshape(x, [-1, 1000, 20, 1])

    conv1 = tf.layers.conv2d(inputs=net, filters=30, kernel_size=3,
                             padding="same", activation=tf.nn.relu)

    conv2 = tf.layers.conv2d(inputs=conv1, filters=64, kernel_size=5,
                             padding="same", activation=tf.nn.relu)

    if params['pooling']:

        pool = tf.layers.max_pooling2d(inputs=conv2, pool_size=(2, 2), strides=2)

    else:
        pool = conv2

    # attempt with tf.keras.layers.concatenate -- FAILURE
    # lstm_f = tf.keras.layers.LSTM(pool, dropout=0.4)()
    # lstm_b = tf.keras.layers.LSTM(pool, dropout=0.4, go_backwards=True)
    # concat_lstm = tf.keras.layers.concatenate((lstm_f, lstm_b))

    # attempt with tf.keras.layers.Bidirectional -- FAILURE
    lstm_fb = tf.keras.layers.LSTM(pool, dropout=0.4)

    concat_lstm = tf.keras.layers.Bidirectional(lstm_fb.input_shape)(lstm_fb)

    dense_1 = tf.layers.dense(inputs=concat_lstm, activation=tf.nn.relu, units=1024)

    dropout = tf.layers.dropout(inputs=dense_1, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

    # last layer with no activation function

    logits = tf.layers.dense(dropout, units=params['n_classes'])

    y_pred = tf.nn.softmax(logits=logits)

    y_pred_cls = tf.argmax(y_pred, axis=1)

    if mode == tf.estimator.ModeKeys.PREDICT:

        spec = tf.estimator.EstimatorSpec(mode=mode, predictions=y_pred_cls)

    else:

        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels,
                                                                       logits=logits)

        loss = tf.reduce_mean(cross_entropy)

        optimizer = tf.train.AdamOptimizer(learning_rate=params["learning_rate"])

        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())

        # Define the evaluation metrics,
        # in this case the classification accuracy.
        metrics = \
            {
                "accuracy": tf.metrics.accuracy(labels, y_pred_cls)
            }

        accuracy = tf.contrib.metrics.accuracy(labels, tf.cast(y_pred_cls, tf.int32))

        logging_hooks = tf.train.LoggingTensorHook({'accuracy': accuracy}, every_n_iter=10)

        # Wrap all of this in an EstimatorSpec.
        spec = tf.estimator.EstimatorSpec(
            mode=mode,
            loss=loss,
            train_op=train_op,
            eval_metric_ops=metrics,
            training_chief_hooks=[logging_hooks])

    return spec


def cnn_2x_lstm(features, labels, mode, params):
    x = features['X']

    # 2 series of 2 cnn layers on ReLU and a forward-backward lstm layer

    # conv2d layers expect 4-dim tensors, reshaping our 3-dim vect

    net = tf.reshape(x, [-1, 1000, 20, 1])

    conv1 = tf.layers.conv2d(inputs=net, filters=30, kernel_size=3,
                             padding="same", activation=tf.nn.relu)

    conv2 = tf.layers.conv2d(inputs=conv1, filters=64, kernel_size=5,
                             padding="same", activation=tf.nn.relu)

    if params['pooling']:

        pool = tf.layers.max_pooling2d(inputs=conv2, pool_size=(2, 2), strides=2)

    else:
        pool = conv2

    concat_lstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(pool, dropout=0.4))

    dense_1 = tf.layers.dense(inputs=concat_lstm, activation=tf.nn.relu, units=1024)

    dropout = tf.layers.dropout(inputs=dense_1, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

    # last layer with no activation function

    logits = tf.layers.dense(dropout, units=params['n_classes'])

    y_pred = tf.nn.softmax(logits=logits)

    y_pred_cls = tf.argmax(y_pred, axis=1)

    if mode == tf.estimator.ModeKeys.PREDICT:

        spec = tf.estimator.EstimatorSpec(mode=mode, predictions=y_pred_cls)

    else:

        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels,
                                                                       logits=logits)

        loss = tf.reduce_mean(cross_entropy)

        optimizer = tf.train.AdamOptimizer(learning_rate=params["learning_rate"])

        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())

        # Define the evaluation metrics,
        # in this case the classification accuracy.
        metrics = \
            {
                "accuracy": tf.metrics.accuracy(labels, y_pred_cls)
            }

        accuracy = tf.contrib.metrics.accuracy(labels, tf.cast(y_pred_cls, tf.int32))

        logging_hooks = tf.train.LoggingTensorHook({'accuracy': accuracy}, every_n_iter=10)

        # Wrap all of this in an EstimatorSpec.
        spec = tf.estimator.EstimatorSpec(
            mode=mode,
            loss=loss,
            train_op=train_op,
            eval_metric_ops=metrics,
            training_chief_hooks=[logging_hooks])

    return spec

import numpy as np
import tensorflow as tf

from util.default_util import *
from util.language_model_util import *

__all__ = ["Embedding", "PretrainedEmbedding"]

class Embedding(object):
    """Embedding layer"""
    def __init__(self,
                 vocab_size,
                 embed_dim,
                 num_gpus=1,
                 default_gpu_id=0,
                 regularizer=None,
                 random_seed=0,
                 trainable=True,
                 scope="embedding"):
        """initialize embedding layer"""
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.regularizer = regularizer if trainable == True else None
        self.random_seed = random_seed
        self.trainable = trainable
        self.scope = scope
        self.device_spec = get_device_spec(default_gpu_id, num_gpus)
        
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            initializer = create_variable_initializer("glorot_uniform", self.random_seed)
            self.embedding = tf.get_variable("embedding", shape=[self.vocab_size, self.embed_dim],
                initializer=initializer, regularizer=self.regularizer, trainable=self.trainable, dtype=tf.float32)
            self.embedding_placeholder = None
    
    def __call__(self,
                 input_data):
        """call embedding layer"""
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            output_embedding = tf.nn.embedding_lookup(self.embedding, input_data)
        
        return output_embedding
    
    def get_embedding_placeholder(self):
        """get pretrained embedding placeholder"""
        return self.embedding_placeholder

class PretrainedEmbedding(object):
    """Pretrained Embedding layer"""
    def __init__(self,
                 vocab_size,
                 embed_dim,
                 embedding,
                 num_gpus=1,
                 default_gpu_id=0,
                 regularizer=None,
                 feedable=True,
                 trainable=True,
                 scope="pretrained_embedding"):
        """initialize pretrained embedding layer"""
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.embedding = embedding
        self.regularizer = regularizer if trainable == True else None
        self.feedable = feedable
        self.trainable = trainable
        self.scope = scope
        self.device_spec = get_device_spec(default_gpu_id, num_gpus)
        
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            if self.embedding is not None:
                initializer = tf.constant_initializer(self.embedding)
                embedding = tf.get_variable("pretrained_embedding", shape=[self.vocab_size, self.embed_dim],
                    initializer=initializer, regularizer=self.regularizer, trainable=self.trainable, dtype=tf.float32)
            else:
                initializer = create_variable_initializer("zero")
                embedding = tf.get_variable("pretrained_embedding", shape=[self.vocab_size, self.embed_dim],
                    initializer=initializer, regularizer=self.regularizer, trainable=self.trainable, dtype=tf.float32)
            
            if self.feedable == True:
                self.embedding_placeholder = tf.placeholder(name="embedding_placeholder",
                    shape=[self.vocab_size, self.embed_dim], dtype=tf.float32)
                self.embedding = embedding.assign(self.embedding_placeholder)
            else:
                self.embedding_placeholder = None
                self.embedding = embedding
    
    def __call__(self,
                 input_data):
        """call pretrained embedding layer"""
        with tf.variable_scope(self.scope, reuse=tf.AUTO_REUSE), tf.device(self.device_spec):
            output_embedding = tf.nn.embedding_lookup(self.embedding, input_data)
        
        return output_embedding
    
    def get_embedding_placeholder(self):
        """get pretrained embedding placeholder"""
        return self.embedding_placeholder

# -*- coding: utf-8 -*-
"""
Multi-GPU examples
==================

数据并行是指当我们将 mini-batch 的样本分成更小的
mini-batches, 并行地计算每个更小的 mini-batches.

数据并行通过使用 ``torch.nn.DataParallel`` 实现.
我们可以用 ``DataParallel`` 包装一个模块,  然后它将在 batch 维度(默认是0轴)
平分数据给多个 GPUs 进行并行计算.

DataParallel
-------------
"""
import torch.nn as nn


class DataParallelModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.block1 = nn.Linear(10, 20)

        # 用 DataParallel 包装 block2
        self.block2 = nn.Linear(20, 20)
        self.block2 = nn.DataParallel(self.block2)

        self.block3 = nn.Linear(20, 20)

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        return x

########################################################################
# 这个代码不做任何修改，在 CPU 模式下也能运行.
#
# DataParallel 的文档为
# `here <http://pytorch.org/docs/nn.html#torch.nn.DataParallel>`_.
#
# **在其上实现 DataParallel 的基元:**
#
#
# 通常, pytorch 的 `nn.parallel` 原函数可以单独使用.
# 我们实现了简单的类似 MPI 的原函数:
#
# - replicate: 在多个设备上复制模块
# - scatter: 在第一维中分配输入
# - gather: 在第一维 gather 和 concatenate 输入
# - parallel\_apply: 将一组已经分配的输入应用于一组已经分配的模型.
#
# 为了更清晰起见, 这里使用这些集合组成的函数 ``data_parallel``

def data_parallel(module, input, device_ids, output_device=None):
    if not device_ids:
        return module(input)

    if output_device is None:
        output_device = device_ids[0]

    replicas = nn.parallel.replicate(module, device_ids)
    inputs = nn.parallel.scatter(input, device_ids)
    replicas = replicas[:len(inputs)]
    outputs = nn.parallel.parallel_apply(replicas, inputs)
    return nn.parallel.gather(outputs, output_device)

########################################################################
# Part of the model on CPU and part on the GPU
# --------------------------------------------
#
# 让我们来看一个网络模型，他的网络一部分用 CPU 运算，另一部分用 GPU 运算。


class DistributedModel(nn.Module):

    def __init__(self):
        super().__init__(
            embedding=nn.Embedding(1000, 10),
            rnn=nn.Linear(10, 10).cuda(0),
        )

    def forward(self, x):
        # 在 CPU 上计算 embedding
        x = self.embedding(x)

        # 迁移到 GPU
        x = x.cuda(0)

        # 在 GPU 上运行 RNN
        x = self.rnn(x)
        return x

########################################################################
#
# 这是面向 Torch 使用者的 PyTorch 的简短介绍.
# 当然还有更多东西需要学习.
#
# 看完这部分教程，也可以看看我们更全面的入门教程, 它介绍了 ``optim`` package,
# data loaders 等.: :doc:`/beginner/deep_learning_60min_blitz`.
#
# 也可以看看
#
# -  :doc:`训练一个会玩视频游戏的神经网络 </intermediate/reinforcement_q_learning>`
# -  `使用imagenet图像数据来训练一个现在最热门的模型`_
# -  `训练一个GAN网络来生成人脸`_
# -  `使用循环神经网络LSTM来训练word-level language模型`_
# -  `了解更多的例子`_
# -  `了解更多的教程`_
# -  `在Forums上讨论PyTorch`_
# -  `在slack和其他用户讨论PyTorch`_
#
# .. _`Deep Learning with PyTorch: a 60-minute blitz`: https://github.com/pytorch/tutorials/blob/master/Deep%20Learning%20with%20PyTorch.ipynb
# .. _Train a state-of-the-art ResNet network on imagenet: https://github.com/pytorch/examples/tree/master/imagenet
# .. _Train an face generator using Generative Adversarial Networks: https://github.com/pytorch/examples/tree/master/dcgan
# .. _Train a word-level language model using Recurrent LSTM networks: https://github.com/pytorch/examples/tree/master/word_language_model
# .. _More examples: https://github.com/pytorch/examples
# .. _More tutorials: https://github.com/pytorch/tutorials
# .. _Discuss PyTorch on the Forums: https://discuss.pytorch.org/
# .. _Chat with other users on Slack: http://pytorch.slack.com/messages/beginner/

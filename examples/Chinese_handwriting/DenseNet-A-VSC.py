# Copyright 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import torch
import torch.legacy.nn as nn
import sparseconvnet.legacy as scn
from data import getIterators

dtype = 'torch.FloatTensor'
dtype = 'torch.cuda.FloatTensor'  # Uncomment this to run on GPU

# two-dimensional SparseConvNet
model = nn.Sequential()
sparseModel = scn.Sequential()
denseModel = nn.Sequential()
model.add(sparseModel).add(denseModel)
sparseModel.add(scn.ValidConvolution(2, 3, 16, 3, False))\
    .add(scn.SparseDenseNet(2, 16, [
        {'pool': 'MP', 'compression': 0},
        {'nExtraLayers': 2, 'growthRate': 16},
        {'pool': 'BN-R-C-AP', 'compression': 0},
        {'nExtraLayers': 2, 'growthRate': 16},
        {'pool': 'BN-R-C-AP', 'compression': 0},
        {'nExtraLayers': 2, 'growthRate': 16},
        {'pool': 'BN-R-C-AP', 'compression': 0},
        {'nExtraLayers': 2, 'growthRate': 16}]))
n_out = sparseModel.modules[-1].nOutputPlanes
sparseModel.add(scn.Convolution(2, n_out, 256, 4, 1, False))
sparseModel.add(scn.BatchNormReLU(256))
sparseModel.add(scn.SparseToDense(2))
denseModel.add(nn.View(-1, 256))
denseModel.add(nn.Linear(256, 3755))
model.type(dtype)
print(model)

spatial_size = sparseModel.suggestInputSize(torch.LongTensor([1, 1]))
print('input spatial size', spatial_size)
dataset = getIterators(spatial_size, 64, 2)
scn.ClassificationTrainValidate(
    model, dataset,
    {'nEpochs': 100, 'initial_LR': 0.1, 'LR_decay': 0.05, 'weightDecay': 1e-4})

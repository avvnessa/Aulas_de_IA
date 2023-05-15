# -*- coding: utf-8 -*-
"""Knn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NjCy4sqyBq_b3OtWp3Cc0xt0LITJTLdd

##Basic requeriments

---
"""

!pip install git+https://github.com/deepvision-class/starter-code

"""## Initial Setup


---
"""

import coutils
import torch
import torchvision
import matplotlib.pyplot as plt
import statistics

plt.rcParams['figure.figsize'] = (10.0, 8.0)
plt.rcParams['font.size'] = 16

"""## Load Dataset  
---
"""

x_train, y_train, x_test, y_test = coutils.data.cifar10()
print('Training set:', )
print('  data shape:', x_train.shape)
print('  labels shape: ', y_train.shape)
print('Test set:')
print('  data shape: ', x_test.shape)
print('  labels shape', y_test.shape)

"""##Visualize the dataset
---
"""

import random 
from torchvision.utils import make_grid

classes = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
samples_per_class = 5
samples = []

for y, cls in enumerate(classes):
  plt.text(-4, 34 * y + 18, cls, ha='right')
  idxs = (y_train == y).nonzero().view(-1)
  for i in range(samples_per_class):
    idx = idxs[random.randrange(idxs.shape[0])].item()
    samples.append(x_train[idx])

img = torchvision.utils.make_grid(samples, nrow=samples_per_class)
plt.imshow(coutils.tensor_to_image(img))
plt.axis('off')
plt.show()

"""## Subsample the dataset
---
"""

num_train = 1000
num_test = 500

x_train, y_train, x_test, y_test = coutils.data.cifar10(num_train, num_test)

print('Training set:', )
print('  data shape:', x_train.shape)
print('  labels shape: ', y_train.shape)
print('Test set:')
print('  data shape: ', x_test.shape)
print('  labels shape', y_test.shape)

"""## Compute distances
---
"""

def compute_distances_two_loops(x_train, x_test):
  num_train = x_train.shape[0]
  num_test = x_test.shape[0]
  dists = x_train.new_zeros(num_train, num_test)
  ############
  for i in range(num_train):
    for j in range(num_test):
      dists[i,j] = ((x_train[i] -x_test[j])**2).sum()**(1/2)
  ############
  return dists

num_train = 1000
num_test = 500

x_train, y_train, x_test, y_test = coutils.data.cifar10(num_train, num_test)
dists = compute_distances_two_loops(x_train, x_test)
print('dists shape', dists.shape)

def compute_distances_one_loop(x_train, x_test):
  num_train = x_train.shape[0]
  num_test = x_test.shape[0]
  dists = x_train.new_zeros(num_train, num_test)
  ###########
  for i in range(num_train):
      dists[i] = ((x_train[i] -x_test)**2).sum(dim  = (1,2,3))**(1/2)
  ###########
  return dists

torch.manual_seed(0)
x_train_rand = torch.randn(100, 3, 16, 16, dtype=torch.float64)
x_test_rand = torch.randn(100, 3, 16, 16, dtype=torch.float64)

dists_one = compute_distances_one_loop(x_train_rand, x_test_rand)
dists_two = compute_distances_two_loops(x_train_rand, x_test_rand)
difference = (dists_one - dists_two).pow(2).sum().sqrt().item()

def compute_distances_no_loops(x_train, x_test):
  num_train = x_train.shape[0]
  num_test = x_test.shape[0]
  dists = x_train.new_zeros(num_train, num_test)
  #################################
  A = x_train.reshape(num_train,-1)
  B = x_test.reshape(num_test,-1)
  AB2 = A.mm(B.T)*2
  #################################
  dists = ((A**2).sum(dim = 1).reshape(-1,1) - AB2 + (B**2).sum(dim = 1).reshape(1,-1))**(1/2)
  return dists

def predict_labels(dists, y_train, k=1):
  num_train, num_test = dists.shape
  y_pred = torch.zeros(num_test, dtype=torch.int64)
  #############
  values, indices = torch.topk(dists, k, dim=0, largest=False)
  for i in range(indices.shape[1]):
    _, idx = torch.max(y_train[indices[:,i]].bincount(), dim = 0)
    y_pred[i] = idx
  #############
  return y_pred

"""##kNN
---
"""

class KnnClassifier:
  def __init__(self, x_train, y_train):
    self.x_train = x_train.contiguous()
    self.y_train = y_train.contiguous()
  def predict(self, x_test, k=1):
    dists = compute_distances_one_loop(self.x_train, x_test.contiguous())
    y_test_pred = predict_labels(dists, self.y_train, k=k)
    return y_test_pred
  def check_accuracy(self, x_test, y_test, k=1, quiet=False):
    y_test_pred = self.predict(x_test, k=k)
    num_samples = x_test.shape[0]
    num_correct = (y_test == y_test_pred).sum().item()
    accuracy = 100.0 * num_correct / num_samples
    msg = (f'Got {num_correct} / {num_samples} correct; '
           f'accuracy is {accuracy:.2f}%')
    if not quiet:
      print(msg)
    return accuracy

num_train = 10000
num_test = 2000
x_train, y_train, x_test, y_test = coutils.data.cifar10(num_train, num_test)

classifier = KnnClassifier(x_train, y_train)
classifier.check_accuracy(x_test, y_test, k=4)
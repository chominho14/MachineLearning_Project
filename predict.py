# -*- coding: utf-8 -*-
"""machine_learning_project_predict.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nD5yvI9U3sSGPunCsc4vRTXohdXlHNXU
"""

from google.colab import drive
drive.mount('/content/drive')

import torch
import torch.nn as nn

import sys
import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.datasets import ImageFolder

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = torch.device("cpu")
print('Device:', device)

data_transform = transforms.Compose([transforms.Resize((224,224))
                                       ,transforms.ToTensor()
                                       ,transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

import torchvision
from torchvision import transforms

testset = torchvision.datasets.ImageFolder(root = "/content/drive/MyDrive/test_data/", transform = data_transform)

testset.__getitem__(40)

print(len(testset))
print(testset[0][0].size())

classes = testset.classes
class_names_to_idx = testset.class_to_idx
print(classes)
print(class_names_to_idx)

torch.manual_seed(1)
test_loader = DataLoader(testset, batch_size=5, shuffle=True, num_workers=0)

print(len(test_loader))

# 실험용 데이터와 결과 출력

from torchvision import transforms, utils
# Get a batch of training data
images, labels = next(iter(test_loader))
print(images.shape)
print(labels.shape)
# Make a grid from batch
img_grid = utils.make_grid(images)

print('GroundTruth: ', ' '.join('%5s' % classes[labels[j]] for j in range(5)))

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels = 3, out_channels = 16, kernel_size=(5, 5), stride=2, padding=1)
        self.conv2 = nn.Conv2d(in_channels = 16, out_channels = 32, kernel_size=(5, 5), stride=2, padding=1)
        self.conv3 = nn.Conv2d(in_channels = 32, out_channels = 64, kernel_size=(3, 3), padding=1)
        self.fc1 = nn.Linear(in_features= 64 * 6 * 6, out_features=500)
        self.fc2 = nn.Linear(in_features=500, out_features=50)
        self.fc3 = nn.Linear(in_features=50, out_features=3)


    def forward(self, X):
        X = F.relu(self.conv1(X))
        X = F.max_pool2d(X, 2)

        X = F.relu(self.conv2(X))
        X = F.max_pool2d(X, 2)

        X = F.relu(self.conv3(X))
        X = F.max_pool2d(X, 2)

        # print(X.shape)
        X = X.view(X.shape[0], -1)
        X = F.relu(self.fc1(X))
        X = F.relu(self.fc2(X))
        X = self.fc3(X)
        nn.Softmax(dim=-1)
        return X

# 저장된 모델 불러오기
test_results = []
grad_image = []

model = CNN()
model.to(device)

checkpoint = torch.load('/content/model4.pt', map_location=torch.device('cuda'))
model.load_state_dict(checkpoint, strict=False)

model.eval()


all_predictions = []
true_labels = []

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        all_predictions.extend(predicted.cpu().numpy())
        true_labels.extend(labels.cpu().numpy())

# 정확도 계산
correct = sum([1 if p == t else 0 for p, t in zip(all_predictions, true_labels)])
accuracy = correct / len(true_labels)
print(f"Accuracy: {accuracy * 100:.2f}%")
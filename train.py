# -*- coding: utf-8 -*-
"""machine_learning_project_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m7mGd_0gL6i0X7ouenSzC2Jb54p4wzlb
"""

from google.colab import drive
drive.mount('/content/drive')

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

# 데이터 변환
data_transform = transforms.Compose([transforms.Resize((224,224))
                                       ,transforms.ToTensor()
                                       ,transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])

import torchvision
from torchvision import transforms

# train과 valid 데이터 변환하여 가져오기
trainset = torchvision.datasets.ImageFolder(root = "/content/drive/MyDrive/train/", transform = data_transform)
validset = torchvision.datasets.ImageFolder(root = "/content/drive/MyDrive/val/", transform = data_transform)

trainset.__getitem__(100)
validset.__getitem__(10)

# train과 valid의 데이터 갯수
print(len(trainset))
print(len(validset))
print(trainset[0][0].size())
print(validset[0][0].size())

# wine, soju, sake 3개의 classes를 가진다.
classes = trainset.classes
class_names_to_idx = trainset.class_to_idx
print(classes)
print(class_names_to_idx)

# train, valid 데이터를 섞어 가져온다.
torch.manual_seed(1)
train_loader = DataLoader(trainset, batch_size=4, shuffle=True, num_workers=0)
valid_loader = DataLoader(validset, batch_size=4, shuffle=True, num_workers=0)

print(len(train_loader))
print(len(valid_loader))

import matplotlib.pyplot as plt
import numpy as np

def imshow(img):
    """Imshow for Tensor."""
#    print(img.shape)
    img = img.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img = std * img + mean
    img = np.clip(img, 0, 1)
#    print("max: {}, min: {}".format(np.max(img), np.min(img)))
    plt.imshow(img)
#    print(img.shape)

imshow(trainset[0][0])

from torchvision import transforms, utils
# Get a batch of training data
images, labels = next(iter(train_loader))
print(images.shape)
print(labels.shape)
# Make a grid from batch
img_grid = utils.make_grid(images)
imshow(img_grid)

# CNN을 사용 (3게의 convolusion layer, relu)
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

torch.manual_seed(1)
model = CNN().to(device)
model

# Optimizer

# 1. Adam
# optimizer = optim.Adam(model.parameters(), lr=0.001)

# 2. SGD
# optimizer = optim.SGD(model.parameters(), lr=1e-4)

# 3. AdaGrad
# optimizer = optim.Adagrad(model.parameters(), lr=0.001)

# 4. RMsprop
optimizer = optim.RMSprop(model.parameters(), lr=0.001)

# 손실함수 다중 분류(CrossEntropyLoss)
loss_function = nn.CrossEntropyLoss()

# epoch를 10과 20 두 개를 사용하여 차이를 비교한다.
n_epochs = 20
best = 0

train_losses=[]
valid_losses=[]
train_accuracy=[]
valid_accuracy=[]

for epoch in range(n_epochs):
    epoch_loss = 0
    epoch_accuracy = 0

    for images, labels in train_loader:
        optimizer.zero_grad()
        images=images.to(device)
        labels=labels.to(device)
        outputs = model(images)
        loss = loss_function(outputs, labels)


        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()/len(train_loader)
        acc = ((outputs.argmax(dim=1) == labels).float().mean())
        epoch_accuracy += acc.item()/len(train_loader)

    train_losses.append(epoch_loss)
    train_accuracy.append(epoch_accuracy)
    print('Epoch : {}, train loss : {:.5f}, train accuracy : {:.5f}'.format(epoch+1, epoch_loss, epoch_accuracy))

    with torch.no_grad():
        epoch_val_accuracy=0
        epoch_val_loss =0
        for images, labels in valid_loader:
            images=images.to(device)
            labels=labels.to(device)
            val_outputs = model(images)
            val_loss = loss_function(val_outputs,labels)

            epoch_val_loss += val_loss/ len(valid_loader)
            acc = ((val_outputs.argmax(dim=1) == labels).float().mean())
            epoch_val_accuracy += acc.item()/ len(valid_loader)

        valid_losses.append(epoch_val_loss)
        valid_accuracy.append(epoch_val_accuracy)

        print('Epoch : {}, valid loss : {:.5f}, valid accuracy : {:.5f}'.format(epoch+1, epoch_val_loss, epoch_val_accuracy))

        # if acc > best:

state = {
    'net' : model.state_dict(),
    'acc' : acc,
    'epoch':epoch
}

torch.save(state, '/content/model.pt')
best = acc

# train의 loss
import matplotlib.pylab as plt
print(train_losses)
plt.plot(range(n_epochs),train_losses, label="train")


plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# valid의 loss
import matplotlib.pylab as plt


print(valid_losses)
val_losses = torch.stack(valid_losses).cpu()

plt.title("Train and Valid Loss")

plt.plot(range(n_epochs),val_losses, label="valid")

#plot the accuracy function
import matplotlib.pylab as plt

plt.title("Valid accuracy")

plt.plot(range(n_epochs),valid_accuracy, label="valid")
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
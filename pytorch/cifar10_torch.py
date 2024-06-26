## Performing image classification on the CIFAR-10 dataset

import torch
import torch.nn as nn
import torchvision
from torchvision import transforms
import torch.nn.functional as F

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# Loading and processing the dataset

transform = transforms.Compose([
    transforms.Resize(size=(32, 32)),
    transforms.Grayscale(1),
    transforms.ToTensor(),
    transforms.Normalize(0.5, 0.5) # Mean and standard deviation used in the proessing of image net
])

trainset = torchvision.datasets.CIFAR10(
    root = "./data",
    train = True,
    download = False,
    transform = transform,
    target_transform = None
)
testset = torchvision.datasets.CIFAR10(
    root = './data',
    train = False,
    download = False,
    transform = transform,
    target_transform = None
)

trainloader = torch.utils.data.DataLoader(
    dataset = trainset,
    batch_size = 32,
    shuffle = True
)
testloader = torch.utils.data.DataLoader(
    dataset = testset,
    batch_size = 32,
    shuffle = True
)

# Creating the Convolution Model
class cifar10Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 12, kernel_size=(3, 3), padding=0, stride=1)
        self.pool1 = nn.AvgPool2d(kernel_size=(2, 2))
        self.flat = nn.Flatten()
        self.dense1 = nn.Linear(2700, 512)
        self.drop1 = nn.Dropout(p=0.2)
        self.dense2 = nn.Linear(512, 64)
        self.dense3 = nn.Linear(64, 10)
    def forward (self, x):
        x = self.pool1(self.conv1(x))
        x = F.relu(x)
        x = self.flat(x)
        x = F.relu(self.dense1(x))
        x = self.drop1(x)
        x = F.relu(self.dense2(x))
        # x = F.log_softmax(self.dense3(x))
        x = self.dense3(x)
        return x

model = cifar10Model().to(device)
loss_fn = nn.CrossEntropyLoss()
opt = torch.optim.SGD(params = model.parameters(), lr=0.01, momentum=0.9)

# Training loop
epochs = 20

for epoch in range(epochs):
    running_loss = 0.0
    model.train()
    for i, (image, labels) in enumerate(trainloader):
        image, labels = image.to(device), labels.to(device)
        opt.zero_grad()
        y_pred = model(image)
        # loss = F.cross_entropy(y_pred, labels)
        # loss = F.nll_loss(y_pred, labels)
        loss = loss_fn(y_pred, labels)
        loss.backward()
        opt.step()
        # Print the loss every 2000 mini batches
        running_loss += loss
        if i%100==99:
            print(f"Epoch {epoch+1}/{epochs}({i+1}/{len(trainloader)}) | Training Loss: {running_loss/100}")
            running_loss = 0.0 # Reset the running loss


    # Validation loop
    model.eval()
    test_loss = 0
    correct = 0
    total = 0

    with torch.inference_mode():
        for i, (test_image, test_labels) in enumerate(testloader):
            test_image, test_labels = test_image.to(device), test_labels.to(device)
            y_test = model(test_image)
            test_loss += loss_fn(y_test, test_labels).item()
            _, predicted = torch.max(y_test.data, 1)
            total += test_labels.size(0)
            correct += (predicted == test_labels).sum().item()

    test_loss = test_loss / len(testloader)
    test_acc = correct / total

    print(f"Validation loss after epoch {epoch+1}: {test_loss} | Validation Accuracy: {test_acc*100}%")

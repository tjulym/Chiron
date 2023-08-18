import numpy as np
import torch
from torch import nn
import random
from sklearn import preprocessing

min_max_scalar = preprocessing.MinMaxScaler()


def run_train_lstm(workflow):
    inp_dim = 17
    out_dim = 1
    mid_dim = 8
    mid_layers = 1
    batch_size = 5
    mod_dir = 'models'

    '''load data'''
    train_x, train_y = load_data(workflow, "train")
    test_x, test_y = load_data(workflow, "test")

    '''build model'''
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = RegLSTM(inp_dim, out_dim, mid_dim, mid_layers).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-2)

    '''train'''
    var_x = torch.tensor(train_x, dtype=torch.float32, device=device)
    var_y = torch.tensor(train_y, dtype=torch.float32, device=device)

    print("Training Start")
    for e in range(2048):
        # out = net(batch_var_x)
        out = net(var_x)
    
        # loss = criterion(out, batch_var_y)
        loss = criterion(out, var_y)
    
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
        if e % 64 == 0:
            print('Epoch: {:4}, Loss: {:.5f}'.format(e, loss.item()))
    torch.save(net.state_dict(), '{}/{}-net.pth'.format(mod_dir, workflow))
    print("Save in:", '{}/net.pth'.format(mod_dir))

    '''eval'''
    net.load_state_dict(torch.load('{}/{}-net.pth'.format(mod_dir, workflow), map_location=lambda storage, loc: storage))
    net = net.eval()

    var_test_x = torch.tensor(test_x, dtype=torch.float32, device=device)

    '''simple way but no elegant'''
    test_diffs = []
    pred_y = net(var_test_x)
    #print(pred_y)
    for i in range(len(pred_y)):
        true_value = np.max(test_y[i])
        pred_value = float(torch.max(pred_y[i]).data)
        print(true_value, pred_value)
        test_diffs.append(np.abs(true_value-pred_value)/true_value)

    print("Test Error: {}".format(np.mean(test_diffs)))


class RegLSTM(nn.Module):
    def __init__(self, inp_dim, out_dim, mid_dim, mid_layers):
        super(RegLSTM, self).__init__()

        self.rnn = nn.LSTM(inp_dim, mid_dim, mid_layers)  # rnn
        self.reg = nn.Sequential(
            nn.Linear(mid_dim, mid_dim),
            nn.Tanh(),
            nn.Linear(mid_dim, out_dim),
        )  # regression

    def forward(self, x):
        y = self.rnn(x)[0]  # y, (h, c) = self.rnn(x)

        seq_len, batch_size, hid_dim = y.shape
        y = y.view(-1, hid_dim)
        y = self.reg(y)
        y = y.view(seq_len, batch_size, -1)
        return y

def load_data(workflow, flag):
    with open("data/{}_{}.csv".format(flag, workflow), "r") as f:
        lines = f.readlines()
    random.shuffle(lines)
    data_xx = []
    data_yy = []
    for line in lines:
        line_splits = line.split("\t")
        for split in line_splits[:-1]:
            data_xx.append([float(i) for i in split.split(",")])
        for lat in line_splits[-1].split(","):
            data_yy.append([float(lat)/1000.0])
    
    data_xx = np.array(data_xx)
    data_yy = np.array(data_yy)

    # normalization
    data_xx = min_max_scalar.fit_transform(data_xx)
    #data_yy = min_max_scalar.fit_transform(data_yy)
    #data_x[:, :-1] = min_max_scalar.fit_transform(data_x[:, :-1])

    data_x = []
    data_y = []
    index = 0
    batch_size = 5
    num_batch = len(data_xx) / batch_size
    while index < num_batch:
        data_x.append(data_xx[index*batch_size:(index+1)*batch_size])
        data_y.append(data_yy[index*batch_size:(index+1)*batch_size])
        index += 1

    data_x = np.array(data_x)
    data_y = np.array(data_y)

    return data_x, data_y


if __name__ == '__main__':
    run_train_lstm("sn")
    # run_train_lstm("mr")
    # run_train_lstm("finra")
    # run_train_lstm("SLApp")
    # run_train_lstm("SLAppV")

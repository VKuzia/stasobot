import numpy as np
import torch
import torch.nn as nn


def _one_hot_encode(arr, n_labels):
    one_hot = np.zeros((np.multiply(*arr.shape), n_labels), dtype=np.float32)
    one_hot[np.arange(one_hot.shape[0]), arr.flatten()] = 1.
    one_hot = one_hot.reshape((*arr.shape, n_labels))
    return one_hot


class CharRNN(nn.Module):
    def __init__(self, chars_num, n_hidden=512, n_layers=4, drop_prob=0.4, is_cuda: bool = True):
        super().__init__()
        self.chars_num = chars_num
        self.drop_prob = drop_prob
        self.n_layers = n_layers
        self.n_hidden = n_hidden
        self.is_cuda = is_cuda

        self.lstm = nn.LSTM(
            chars_num, n_hidden, n_layers, dropout=drop_prob, batch_first=True
        )
        self.dropout = nn.Dropout(drop_prob)
        self.linear = nn.Sequential(
            nn.Linear(n_hidden, n_hidden),
            nn.BatchNorm1d(n_hidden),
            nn.ReLU(),
        )
        self.fc = nn.Linear(n_hidden, chars_num)

    def forward(self, x, hidden):
        r_output, hidden = self.lstm(x, hidden)
        out = self.dropout(r_output)
        out = out.contiguous().view(-1, self.n_hidden)
        out = self.linear(out)
        out = self.fc(out)
        return out, hidden

    def init_hidden(self, batch_size):
        weight = next(self.parameters()).data
        if self.is_cuda:
            hidden = (
                weight.new(self.n_layers, batch_size, self.n_hidden).zero_().cuda(),
                weight.new(self.n_layers, batch_size, self.n_hidden).zero_().cuda(),
            )
        else:
            hidden = (
                weight.new(self.n_layers, batch_size, self.n_hidden).zero_(),
                weight.new(self.n_layers, batch_size, self.n_hidden).zero_(),
            )
        return hidden


class Model:
    def __init__(self, path_to_model: str, cuda: bool):
        self._init_alphabet()
        self.kernel = CharRNN(len(self.alphabet), is_cuda=cuda)
        self.kernel.load_state_dict(torch.load(path_to_model,map_location=torch.device('cpu')))
        self.cuda = cuda
        if cuda:
            self.kernel = self.kernel.cuda()

    def generate(self, prime, length, temperature):
        return self._sample(size=length, prime=prime, temperature=temperature, top_k=7)

    def filter(self, text: str) -> str:
        return ''.join([character for character in text if character in self.alphabet])

    def _integerify(self, list_of_strings):
        result = []
        for string in list_of_strings:
            result.append([self.char_to_index[x] for x in string])
        return result

    def _collate_function(self, batch):
        sample_list = self._integerify([first for first, second in batch])
        label_list = self._integerify([second for first, second in batch])
        return torch.tensor(sample_list), torch.tensor(label_list)

    def _init_alphabet(self):
        self.special = '$'
        self.alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" \
                        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ .,!?\n" + self.special
        self.char_to_index = {self.alphabet[i]: i for i in range(len(self.alphabet))}

    def _predict(self, net, char, h=None, temperature=1, top_k=None):
        x = np.array(self._integerify([char]))
        x = _one_hot_encode(x, len(self.alphabet))
        if self.cuda:
            inputs = torch.from_numpy(x).cuda()
        else:
            inputs = torch.from_numpy(x)
        h = tuple([each.data for each in h])
        out, h = net(inputs, h)
        out = torch.exp(temperature * out)
        p = torch.nn.functional.softmax(out, dim=1).data.cpu()
        if top_k is None:
            top_ch = np.arange(len(net.chars))
        else:
            p, top_ch = p.topk(top_k)
            top_ch = top_ch.numpy().squeeze()
        p = p.numpy().squeeze()
        char = np.random.choice(top_ch, p=p / p.sum())
        return self.alphabet[char], h

    def _sample(self, size, prime, temperature=1, top_k=None):
        self.kernel.eval()
        chars = [ch for ch in prime]
        h = self.kernel.init_hidden(1)
        for ch in prime:
            char, h = self._predict(self.kernel, ch, h, temperature, top_k=top_k)
        chars.append(char)
        for ii in range(size):
            char, h = self._predict(self.kernel, chars[-1], h, temperature, top_k=top_k)
            chars.append(char)
        return ''.join(chars)

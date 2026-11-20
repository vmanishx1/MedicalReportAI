import torch
import torch.nn as nn
import torch.nn.functional as F


class CNNEncoder(nn.Module):
    def __init__(self, encoded_image_size=14, encoder_dim=2048):
        super().__init__()
        self.encoded_image_size = encoded_image_size
        self.encoder_dim = encoder_dim

    def forward(self, x):
        return x


class AttentionLayer(nn.Module):
    def __init__(self, encoder_dim, decoder_dim, attention_dim):
        super().__init__()
        self.encoder_att = nn.Linear(encoder_dim, attention_dim)
        self.decoder_att = nn.Linear(decoder_dim, attention_dim)
        self.full_att = nn.Linear(attention_dim, 1)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, encoder_out, decoder_hidden):
        att1 = self.encoder_att(encoder_out)
        att2 = self.decoder_att(decoder_hidden)
        att = self.full_att(self.relu(att1 + att2.unsqueeze(1))).squeeze(2)
        alpha = self.softmax(att)
        context = (encoder_out * alpha.unsqueeze(2)).sum(dim=1)
        return context, alpha


class LSTMDecoderWithAttention(nn.Module):
    def __init__(
        self,
        attention_dim,
        embed_dim,
        decoder_dim,
        vocab_size,
        encoder_dim=2048,
        dropout=0.5,
    ):
        super().__init__()
        self.encoder_dim = encoder_dim
        self.attention_dim = attention_dim
        self.embed_dim = embed_dim
        self.decoder_dim = decoder_dim
        self.vocab_size = vocab_size
        self.dropout = dropout

        self.attention = AttentionLayer(encoder_dim, decoder_dim, attention_dim)
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.dropout_layer = nn.Dropout(p=dropout)
        self.lstm = nn.LSTMCell(embed_dim + encoder_dim, decoder_dim, bias=True)
        self.fc = nn.Linear(decoder_dim, vocab_size)
        self.init_weights()

    def init_weights(self):
        self.embedding.weight.data.uniform_(-0.1, 0.1)
        self.fc.bias.data.fill_(0)
        self.fc.weight.data.uniform_(-0.1, 0.1)

    def init_hidden_state(self, batch_size, device):
        h = torch.zeros(batch_size, self.decoder_dim).to(device)
        c = torch.zeros(batch_size, self.decoder_dim).to(device)
        return h, c

    def forward(self, encoder_out, captions, caption_lengths):
        batch_size = encoder_out.size(0)
        encoder_dim = encoder_out.size(-1)
        encoder_out = encoder_out.view(batch_size, -1, encoder_dim)

        vocab_size = self.vocab_size
        embeddings = self.embedding(captions)

        h, c = self.init_hidden_state(batch_size, encoder_out.device)

        seq_len = captions.size(1) - 1
        predictions = torch.zeros(batch_size, seq_len, vocab_size).to(encoder_out.device)
        alphas = torch.zeros(batch_size, seq_len, encoder_out.size(1)).to(encoder_out.device)

        for t in range(seq_len):
            context, alpha = self.attention(encoder_out, h)
            lstm_input = torch.cat([embeddings[:, t, :], context], dim=1)
            h, c = self.lstm(lstm_input, (h, c))
            preds = self.fc(self.dropout_layer(h))
            predictions[:, t, :] = preds
            alphas[:, t, :] = alpha

        return predictions, alphas

    def generate(self, encoder_out, start_token, end_token, max_len=50, beam_size=3):
        batch_size = encoder_out.size(0)
        encoder_dim = encoder_out.size(-1)
        encoder_out = encoder_out.view(batch_size, -1, encoder_dim)

        h, c = self.init_hidden_state(batch_size, encoder_out.device)

        tokens = torch.full((batch_size, 1), start_token, dtype=torch.long).to(encoder_out.device)
        result = tokens.clone()

        for _ in range(max_len):
            embeddings = self.embedding(tokens[:, -1])
            context, alpha = self.attention(encoder_out, h)
            lstm_input = torch.cat([embeddings, context], dim=1)
            h, c = self.lstm(lstm_input, (h, c))
            preds = self.fc(h)
            next_token = preds.argmax(dim=-1, keepdim=True)
            result = torch.cat([result, next_token], dim=-1)
            if (next_token == end_token).all():
                break

        return result


class ReportGenerationModel(nn.Module):
    def __init__(
        self,
        vocab_size=5000,
        encoder_dim=2048,
        decoder_dim=512,
        embed_dim=256,
        attention_dim=256,
        dropout=0.5,
    ):
        super().__init__()
        self.encoder = CNNEncoder(encoder_dim=encoder_dim)
        self.decoder = LSTMDecoderWithAttention(
            attention_dim=attention_dim,
            embed_dim=embed_dim,
            decoder_dim=decoder_dim,
            vocab_size=vocab_size,
            encoder_dim=encoder_dim,
            dropout=dropout,
        )

    def forward(self, images, captions, caption_lengths):
        features = self.encoder(images)
        predictions, alphas = self.decoder(features, captions, caption_lengths)
        return predictions, alphas

    def generate_report(self, features, start_token=1, end_token=2, max_len=100):
        return self.decoder.generate(features, start_token, end_token, max_len)

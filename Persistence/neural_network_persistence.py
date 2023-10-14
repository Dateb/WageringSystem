import torch

NEURAL_NETWORK_PATH = "../data/best_neural_network"


def save(neural_network) -> None:
    checkpoint = {'model_state_dict': neural_network.state_dict()}
    torch.save(checkpoint, NEURAL_NETWORK_PATH)


def load_state_into_neural_network(neural_network) -> None:
    checkpoint = torch.load(NEURAL_NETWORK_PATH)
    neural_network.load_state_dict(checkpoint['model_state_dict'])

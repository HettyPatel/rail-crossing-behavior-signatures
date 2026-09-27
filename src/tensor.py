import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tensorly.decomposition import parafac, non_negative_parafac
import tensorly as tl
from tensorly.cp_tensor import cp_to_tensor

# Flexible SymCPD using PyTorch (works for any size)
class SymCPD(nn.Module):
    def __init__(
            self, num_crossings, num_timesteps, rank: int,
    ):
        super().__init__()
        self.rank = rank
        self.num_crossings = num_crossings
        self.num_timesteps = num_timesteps
        self.weight = nn.Parameter(torch.ones(rank))
        self.A = nn.Embedding(self.num_crossings, rank)
        self.C = nn.Embedding(self.num_timesteps, rank)

        self.initialize()

    def initialize(self):
        nn.init.kaiming_uniform_(self.A.weight.data)
        nn.init.kaiming_uniform_(self.C.weight.data)

    def forward(self):

        lst = []
        for i in range(self.num_timesteps):
            a = self.A.weight
            c = self.C.weight[i]
            x = a @ torch.diag(c * self.weight) @ a.T
            lst.append(x)

        return torch.stack(lst, 0)


def train(dataset, config, verbose=True):

    lr = config.lr
    wd = config.wd
    n_iter = config.niter

    model = SymCPD(dataset.num_crossings, dataset.num_timesteps, config.rank)
    opt = optim.Adam(model.parameters(), lr=lr, weight_decay=wd)

    loss_history = []

    for i in range(1, n_iter):
        opt.zero_grad()
        rec = model()
        loss = ((rec - dataset.ttensor) **2).sum()
        loss.backward()
        opt.step()

        loss_val = loss.item()
        loss_history.append(loss_val)

        if verbose and i % 100 == 0:
            print(f"Iters: {i} || loss : {loss_val:.4f}")

    model.loss_history = loss_history
    return model


# Non-negative Symmetric CPD using TensorLy
class NonNegativeSymCPD:
    """
    Non-negative Symmetric CPD using TensorLy's non_negative_parafac.
    All factors are constrained to be non-negative for easier interpretation.
    """
    def __init__(self, num_crossings, num_timesteps, rank):
        self.rank = rank
        self.num_crossings = num_crossings
        self.num_timesteps = num_timesteps
        self.weight = None
        self.A = None
        self.C = None
        self.loss_history = []

    def fit(self, tensor_np, n_iter=2000, tol=1e-7, random_state=None, verbose=True):
        """
        Fit non-negative CPD to the tensor.

        Parameters:
        -----------
        tensor_np : numpy array
            Input tensor of shape (num_timesteps, num_crossings, num_crossings)
        n_iter : int
            Maximum number of iterations
        tol : float
            Convergence tolerance
        random_state : int or None
            Random seed for reproducibility
        verbose : bool
            Whether to print progress
        """
        if verbose:
            print(f"Running non-negative CPD (rank={self.rank}, max_iter={n_iter})...")

        # Run non-negative PARAFAC
        # Returns (weights, factors) where factors = [factor_0, factor_1, factor_2]
        weights, factors = non_negative_parafac(
            tensor_np,
            rank=self.rank,
            n_iter_max=n_iter,
            init='random',
            tol=tol,
            random_state=random_state,
            verbose=verbose,
            return_errors=False
        )

        # Extract factors
        self.weight = weights  # Component weights (rank,)
        self.C = factors[0]    # Phase factor (num_timesteps, rank)
        self.A = factors[1]    # Video factor (num_crossings, rank)
        # factors[2] should equal factors[1] for symmetric tensor

        # Note: TensorLy's non_negative_parafac doesn't return per-iteration errors
        # So we'll compute final reconstruction error
        reconstruction = tl.cp_to_tensor((weights, factors))
        error = np.sum((tensor_np - reconstruction) ** 2)
        self.loss_history = [error]  # Only final error available

        if verbose:
            print(f"Converged. Final reconstruction error: {error:.4f}")

        return self

    def get_factors(self):
        """Return the learned factors."""
        return {
            'weight': self.weight,
            'U': self.A,  # Video loadings
            'lambdas': self.C  # Phase importances
        }


def train_nonnegative(dataset, config, verbose=True):
    """
    Train non-negative SymCPD model.

    Parameters:
    -----------
    dataset : TensorDataset
        Dataset containing the tensor
    config : Config
        Configuration with rank, niter
    verbose : bool
        Whether to print progress

    Returns:
    --------
    model : NonNegativeSymCPD
        Trained model
    """
    model = NonNegativeSymCPD(
        dataset.num_crossings,
        dataset.num_timesteps,
        config.rank
    )

    # Convert tensor to numpy for TensorLy
    tensor_np = dataset.ttensor.cpu().numpy()

    # Set random seed if available
    random_state = getattr(config, 'seed', None)

    # Fit the model
    model.fit(
        tensor_np,
        n_iter=config.niter,
        random_state=random_state,
        verbose=verbose
    )

    return model
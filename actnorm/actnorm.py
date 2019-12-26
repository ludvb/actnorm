import torch


__all__ = ["ActNorm1d", "ActNorm2d", "ActNorm3d"]


class ActNorm(torch.jit.ScriptModule):
    def __init__(self, num_features: int):
        super().__init__()
        self.scale = torch.nn.Parameter(torch.zeros(num_features))
        self.bias = torch.nn.Parameter(torch.zeros(num_features))
        self.__initialized = False

    def reset_(self):
        self.__initialized = False
        return self

    def _check_input_dim(self, x: torch.Tensor) -> None:
        raise NotImplementedError()  # pragma: no cover

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        self._check_input_dim(x)
        if x.dim() > 2:
            x = x.transpose(1, -1)
        shape = x.shape
        x = x.reshape(-1, shape[-1])
        if not self.__initialized:
            self.scale.data = 1 / x.detach().std(0, unbiased=False)
            self.bias.data = -self.scale * x.detach().mean(0)
            self.__initialized = True
        x = self.scale * x + self.bias
        x = x.reshape(shape)
        if x.dim() > 2:
            x = x.transpose(1, -1)
        return x


class ActNorm1d(ActNorm):
    def _check_input_dim(self, x: torch.Tensor) -> None:
        if x.dim() not in [2, 3]:
            raise ValueError("expected 2D or 3D input (got {x.dim()}D input)")


class ActNorm2d(ActNorm):
    def _check_input_dim(self, x: torch.Tensor) -> None:
        if x.dim() != 4:
            raise ValueError("expected 4D input (got {x.dim()}D input)")


class ActNorm3d(ActNorm):
    def _check_input_dim(self, x: torch.Tensor) -> None:
        if x.dim() != 5:
            raise ValueError("expected 5D input (got {x.dim()}D input)")

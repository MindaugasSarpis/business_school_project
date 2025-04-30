import torch


async def free_torch_cache(device: str | torch.device) -> None:
    """Frees the PyTorch cache for a given device.

    Args:
        device (str | torch.device): The device to free the cache for.
    """

    if "mps" in str(device):
        torch.mps.empty_cache()
    elif "cuda" in str(device):
        torch.cuda.empty_cache()

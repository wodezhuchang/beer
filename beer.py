import torch
print(torch.version.cuda)  # 如果显示None，说明是CPU版本
print(torch.cuda.is_available())  # 返回False说明GPU不可用


"""
import torch
print("CUDA可用:", torch.cuda.is_available())
print("GPU数量:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("GPU名称:", torch.cuda.get_device_name(0))
    """




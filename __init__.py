import importlib
import os

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 指定 JS 文件的位置
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

# 1. 获取当前文件夹路径
current_dir = os.path.dirname(__file__)

# 2. 遍历当前文件夹下所有的 .py 文件
for filename in os.listdir(current_dir):
    # 排除掉 __init__.py 自身，只加载其他 py 文件
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3] # 去掉 .py 后缀
        
        try:
            # 动态导入模块
            module = importlib.import_module(f".{module_name}", package=__name__)
            
            # 如果模块里有节点映射，就合并进来
            if hasattr(module, "NODE_CLASS_MAPPINGS"):
                NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
                
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
                
            print(f"Loaded custom node: {module_name}")
            
        except Exception as e:
            print(f"Failed to load custom node {filename}: {e}")
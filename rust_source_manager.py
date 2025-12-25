#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rust 源切换管理工具
支持切换 Rust 源，修改 Windows 环境变量和 Cargo 配置文件
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Any
import winreg

try:
    import toml  # pyright: ignore[reportMissingModuleSource]
except ImportError:
    print("错误: 需要安装 toml 库，请运行: pip install toml")
    sys.exit(1)

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False


# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "config"
SOURCES_CONFIG_FILE = CONFIG_DIR / "sources.toml"


def load_sources_config() -> Dict[str, Any]:
    """加载源配置文件"""
    if not SOURCES_CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在: {SOURCES_CONFIG_FILE}")
    
    with open(SOURCES_CONFIG_FILE, 'r', encoding='utf-8') as f:
        return toml.load(f)


def save_sources_config(config: Dict[str, Any]) -> None:
    """保存源配置文件"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(SOURCES_CONFIG_FILE, 'w', encoding='utf-8') as f:
        toml.dump(config, f)


def get_current_source(config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """获取当前使用的源名称"""
    if config is None:
        config = load_sources_config()
    return config.get('current')


def get_source_config(config: Dict[str, Any], source_name: str) -> Dict[str, Any]:
    """获取指定源的配置"""
    sources = config.get('sources', {})
    if source_name not in sources:
        raise ValueError(f"源 '{source_name}' 不存在")
    return sources[source_name]


def update_windows_env_vars(source_config: Dict[str, Any]) -> None:
    """更新 Windows 用户级环境变量"""
    try:
        # 打开用户环境变量注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # 设置环境变量
        rustup_dist_server = source_config.get('rustup_dist_server', '')
        rustup_update_root = source_config.get('rustup_update_root', '')
        
        if rustup_dist_server:
            winreg.SetValueEx(key, "RUSTUP_DIST_SERVER", 0, winreg.REG_SZ, rustup_dist_server)
            print(f"✓ 已设置环境变量 RUSTUP_DIST_SERVER = {rustup_dist_server}")
        
        if rustup_update_root:
            winreg.SetValueEx(key, "RUSTUP_UPDATE_ROOT", 0, winreg.REG_SZ, rustup_update_root)
            print(f"✓ 已设置环境变量 RUSTUP_UPDATE_ROOT = {rustup_update_root}")
        
        winreg.CloseKey(key)
        
        # 提示用户重启终端以使环境变量生效
        # 注意：环境变量已写入注册表，但需要重启终端才能在当前会话中生效
        print("⚠ 提示: 环境变量已写入注册表，请重启终端以使环境变量生效")
        print("   或者手动运行: refreshenv (如果安装了 Chocolatey)")
        
    except Exception as e:
        raise RuntimeError(f"修改 Windows 环境变量失败: {e}")


def get_cargo_config_path() -> Path:
    """获取 Cargo config.toml 文件路径"""
    cargo_home = os.environ.get('CARGO_HOME')
    if cargo_home:
        return Path(cargo_home) / "config.toml"
    else:
        # 默认路径: ~/.cargo/config.toml
        home = Path.home()
        return home / ".cargo" / "config.toml"


def update_cargo_config(source_config: Dict[str, Any]) -> None:
    """更新 Cargo config.toml 文件"""
    try:
        cargo_config_path = get_cargo_config_path()
        cargo_config_dir = cargo_config_path.parent
        
        # 创建目录（如果不存在）
        cargo_config_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取 cargo_config 内容
        cargo_config_content = source_config.get('cargo_config', '').strip()
        
        if not cargo_config_content:
            print("⚠ 警告: 源配置中没有 cargo_config 内容，跳过 Cargo 配置更新")
            return
        
        # 写入配置文件（完全覆盖）
        with open(cargo_config_path, 'w', encoding='utf-8') as f:
            f.write(cargo_config_content)
        
        print(f"✓ 已更新 Cargo 配置文件: {cargo_config_path}")
    except Exception as e:
        raise RuntimeError(f"更新 Cargo 配置文件失败: {e}")


def save_history(prev_source_config: Optional[Dict[str, Any]], current_source_config: Dict[str, Any], prev_source_name: Optional[str] = None, current_source_name: str = '') -> None:
    """保存历史记录"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    history_file = CONFIG_DIR / "history.toml"
    
    history_data = {}
    
    # 保存 previous 配置
    if prev_source_config:
        history_data['previous'] = {
            'name': prev_source_name if prev_source_name else '',
            'rustup_dist_server': prev_source_config.get('rustup_dist_server', ''),
            'rustup_update_root': prev_source_config.get('rustup_update_root', ''),
            'cargo_config': prev_source_config.get('cargo_config', '')
        }
    else:
        history_data['previous'] = {
            'name': '',
            'rustup_dist_server': '',
            'rustup_update_root': '',
            'cargo_config': ''
        }
    
    # 保存 current 配置
    history_data['current'] = {
        'name': current_source_name,
        'rustup_dist_server': current_source_config.get('rustup_dist_server', ''),
        'rustup_update_root': current_source_config.get('rustup_update_root', ''),
        'cargo_config': current_source_config.get('cargo_config', '')
    }
    
    with open(history_file, 'w', encoding='utf-8') as f:
        toml.dump(history_data, f)
    
    print(f"✓ 历史记录已保存: {history_file}")


def has_history() -> bool:
    """检查是否存在历史记录文件"""
    history_file = CONFIG_DIR / "history.toml"
    return history_file.exists()


def switch_source(source_name: str, override_params: Optional[Dict[str, str]] = None) -> None:
    """切换源"""
    # 加载配置
    config = load_sources_config()
    
    # 验证源是否存在
    if source_name not in config.get('sources', {}):
        raise ValueError(f"源 '{source_name}' 不存在。可用源: {', '.join(config.get('sources', {}).keys())}")
    
    # 获取当前源
    prev_source_name = get_current_source(config)
    
    # 获取 previous 源的配置（如果存在）
    prev_source_config = None
    if prev_source_name and prev_source_name in config.get('sources', {}):
        prev_source_config = get_source_config(config, prev_source_name).copy()
    
    # 检查是否为初始化（没有历史记录）
    is_initialization = not has_history()
    
    # 获取源配置
    source_config = get_source_config(config, source_name).copy()
    
    # 应用命令行覆盖参数
    if override_params:
        for key, value in override_params.items():
            if key in source_config:
                source_config[key] = value
                print(f"✓ 已覆盖参数: {key} = {value}")
            else:
                print(f"⚠ 警告: 参数 '{key}' 不存在于源配置中，已忽略")
    
    # 更新环境变量
    if is_initialization:
        print(f"\n正在初始化源: {source_name}")
    else:
        print(f"\n正在切换到源: {source_name}")
    update_windows_env_vars(source_config)
    
    # 更新 Cargo 配置
    update_cargo_config(source_config)
    
    # 更新配置文件中的 current 字段
    config['current'] = source_name
    save_sources_config(config)
    
    # 保存历史记录（传递完整的配置信息）
    save_history(prev_source_config, source_config, prev_source_name, source_name)
    
    if is_initialization:
        print(f"\n✓ 成功初始化源: {source_name}")
    else:
        print(f"\n✓ 成功切换到源: {source_name}")
        if prev_source_name:
            print(f"  之前使用的源: {prev_source_name}")


def list_sources() -> None:
    """列出所有可用源"""
    config = load_sources_config()
    current = get_current_source(config)
    sources = config.get('sources', {})
    
    if not sources:
        print("没有配置任何源")
        return
    
    print("可用源列表:")
    print("-" * 60)
    for name, source_config in sources.items():
        marker = " (当前)" if name == current else ""
        print(f"  {name}{marker}")
        print(f"    RUSTUP_DIST_SERVER: {source_config.get('rustup_dist_server', 'N/A')}")
        print(f"    RUSTUP_UPDATE_ROOT: {source_config.get('rustup_update_root', 'N/A')}")
        print()


def show_current_source() -> None:
    """显示当前使用的源"""
    try:
        config = load_sources_config()
        current = get_current_source(config)
        
        if not current:
            print("当前未设置源")
            return
        
        source_config = get_source_config(config, current)
        
        print(f"当前使用的源: {current}")
        print("-" * 60)
        print(f"RUSTUP_DIST_SERVER: {source_config.get('rustup_dist_server', 'N/A')}")
        print(f"RUSTUP_UPDATE_ROOT: {source_config.get('rustup_update_root', 'N/A')}")
        print(f"\nCargo 配置文件: {get_cargo_config_path()}")
        
    except Exception as e:
        print(f"错误: {e}")


def interactive_select_source() -> Optional[str]:
    """交互式选择源（使用 questionary 库）"""
    if not HAS_QUESTIONARY:
        print("错误: 交互式选择功能需要安装 questionary 库")
        print("请运行: pip install questionary")
        return None
    
    try:
        config = load_sources_config()
        sources = list(config.get('sources', {}).keys())
        current = get_current_source(config)
        
        if not sources:
            print("没有配置任何源")
            return None
        
        # 构建选择项列表，包含源名称和描述信息
        choices = []
        for name in sources:
            source_config = config.get('sources', {}).get(name, {})
            marker = " (当前)" if name == current else ""
            description = f"RUSTUP_DIST_SERVER: {source_config.get('rustup_dist_server', 'N/A')}"
            choices.append(
                questionary.Choice(
                    title=f"{name}{marker}",
                    value=name,
                    description=description
                )
            )
        
        # 使用 questionary 的 select 方法
        selected_source = questionary.select(
            "请选择要切换的源（使用 ↑↓ 键移动，Enter 确认，Ctrl+C 取消）:",
            choices=choices,
            default=current if current and current in sources else None
        ).ask()
        
        return selected_source
        
    except KeyboardInterrupt:
        print("\n已取消选择")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None


def parse_override_params(override_args: list) -> Dict[str, str]:
    """解析覆盖参数"""
    params = {}
    for arg in override_args:
        if '=' not in arg:
            raise ValueError(f"覆盖参数格式错误: {arg}，应为 key=value 格式")
        key, value = arg.split('=', 1)
        params[key.strip()] = value.strip()
    return params


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Rust 源切换管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python rust_source_manager.py --list                    # 列出所有源
  python rust_source_manager.py --show                    # 显示当前源
  python rust_source_manager.py --interactive             # 交互式选择源（推荐）
  python rust_source_manager.py --switch                   # 切换到 current 字段指定的源
  python rust_source_manager.py --switch rsproxy-sparse   # 切换到指定源
  python rust_source_manager.py --switch rsproxy-sparse \\
      --override rustup_dist_server=https://example.com   # 切换并覆盖参数
        """
    )
    
    parser.add_argument(
        '--switch',
        metavar='NAME',
        nargs='?',
        const='__CURRENT__',
        help='切换到指定源（如果不提供参数，则切换到 current 字段指定的源；使用 --interactive 进行交互式选择）'
    )
    
    parser.add_argument(
        '--interactive',
        '-i',
        action='store_true',
        help='交互式选择源（使用上下键移动，Enter 确认，ESC 取消）'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有可用源'
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='显示当前使用的源'
    )
    
    parser.add_argument(
        '--override',
        metavar='KEY=VALUE',
        action='append',
        dest='overrides',
        help='覆盖配置参数（可多次使用，如: --override key1=value1 --override key2=value2）'
    )
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，显示帮助
    if not any([args.switch, args.list, args.show, args.interactive]):
        parser.print_help()
        return
    
    try:
        # 解析覆盖参数
        override_params = None
        if args.overrides:
            override_params = parse_override_params(args.overrides)
        
        # 执行相应操作
        if args.list:
            list_sources()
        elif args.show:
            show_current_source()
        elif args.interactive:
            # 交互式选择源
            selected_source = interactive_select_source()
            if selected_source:
                switch_source(selected_source, override_params)
        elif args.switch is not None:
            # 如果 --switch 没有参数，使用 current 字段指定的源
            if args.switch == '__CURRENT__':
                config = load_sources_config()
                current = get_current_source(config)
                if not current:
                    print("错误: 配置文件中没有设置 current 字段，请指定源名称")
                    sys.exit(1)
                source_name = current
                print(f"使用 current 字段指定的源: {source_name}")
            else:
                source_name = args.switch
            switch_source(source_name, override_params)
    
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print(f"请确保配置文件存在: {SOURCES_CONFIG_FILE}")
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


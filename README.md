# Rust 源切换管理工具

一个用于管理 Rust 源切换的 Python 工具，支持在多个 Rust 镜像源之间快速切换，自动配置 Windows 环境变量和 Cargo 配置文件。

## 功能特性

- 🔄 **多源管理**：支持配置多个 Rust 镜像源（如 rsproxy、xuanwu 等）
- ⚙️ **自动配置**：自动修改 Windows 用户级环境变量和 Cargo 配置文件
- 📝 **历史记录**：每次切换都会生成历史记录文件，方便追溯和回滚
- 🎯 **命令行接口**：提供简洁的命令行接口，支持列表、切换、查看等操作
- 🔧 **参数覆盖**：支持通过命令行参数临时覆盖配置项
- ✅ **错误处理**：完善的错误处理和用户提示

## 安装

### 前置要求

- Python 3.6+
- Windows 操作系统（用于环境变量修改）

### 安装依赖

**推荐使用虚拟环境（推荐）**：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**或者直接安装 toml 库**：

```bash
pip install toml
```

> **注意**：使用虚拟环境可以避免污染全局 Python 环境，推荐使用。

## 使用方法

> **提示**：如果使用虚拟环境，请先激活虚拟环境（见安装步骤）。

### 查看帮助

```bash
python rust_source_manager.py --help
```

### 列出所有可用源

```bash
python rust_source_manager.py --list
```

输出示例：
```
可用源列表:
------------------------------------------------------------
  rsproxy-sparse (当前)
    RUSTUP_DIST_SERVER: https://rsproxy.cn
    RUSTUP_UPDATE_ROOT: https://rsproxy.cn/rustup

  xuanwu-sparse
    RUSTUP_DIST_SERVER: https://mirror.xuanwu.openatom.cn
    RUSTUP_UPDATE_ROOT: https://mirror.xuanwu.openatom.cn/rustup
```

### 显示当前使用的源

```bash
python rust_source_manager.py --show
```

输出示例：
```
当前使用的源: rsproxy-sparse
------------------------------------------------------------
RUSTUP_DIST_SERVER: https://rsproxy.cn
RUSTUP_UPDATE_ROOT: https://rsproxy.cn/rustup

Cargo 配置文件: C:\Users\YourName\.cargo\config.toml
```

### 切换到指定源

**方式一：直接指定源名称**

```bash
python rust_source_manager.py --switch <源名称>
```

示例：
```bash
# 切换到 rsproxy-sparse 源
python rust_source_manager.py --switch rsproxy-sparse

# 切换到 xuanwu-sparse 源
python rust_source_manager.py --switch xuanwu-sparse
```

**方式二：交互式选择（推荐）**

使用 `--interactive` 或 `-i` 参数进入交互式选择模式：

```bash
python rust_source_manager.py --interactive
# 或
python rust_source_manager.py -i
```

> **注意**：交互式选择功能需要安装 `questionary` 库。如果未安装，运行 `pip install questionary` 或 `pip install -r requirements.txt`。

交互式模式功能：
- 使用 **↑** 和 **↓** 键在源列表中移动
- 按 **Enter** 确认选择并切换
- 按 **Ctrl+C** 取消选择
- 当前使用的源会显示 "(当前)" 标记
- 每个源会显示配置信息（RUSTUP_DIST_SERVER）

### 切换并覆盖参数

如果需要临时覆盖某些配置参数，可以使用 `--override` 选项：

```bash
python rust_source_manager.py --switch rsproxy-sparse \
    --override rustup_dist_server=https://example.com \
    --override rustup_update_root=https://example.com/rustup
```

## 配置文件说明

### 源配置文件：`config/sources.toml`

配置文件使用 TOML 格式，包含以下内容：

- `current`: 当前使用的源名称
- `sources`: 所有源的配置字典

每个源配置包含：
- `rustup_dist_server`: Rustup 分发服务器地址
- `rustup_update_root`: Rustup 更新根地址
- `cargo_config`: Cargo 配置文件内容（TOML 格式字符串）

示例配置：

```toml
current = "rsproxy-sparse"

[sources.rsproxy-sparse]
rustup_dist_server = "https://rsproxy.cn"
rustup_update_root = "https://rsproxy.cn/rustup"
cargo_config = """
[source.crates-io]
replace-with = 'rsproxy-sparse'
[source.rsproxy-sparse]
registry = "sparse+https://rsproxy.cn/index/"
[net]
git-fetch-with-cli = true
"""

[sources.xuanwu-sparse]
rustup_dist_server = "https://mirror.xuanwu.openatom.cn"
rustup_update_root = "https://mirror.xuanwu.openatom.cn/rustup"
cargo_config = """
[source.crates-io]
replace-with = 'xuanwu-sparse'
[source.xuanwu]
registry = "https://mirror.xuanwu.openatom.cn/crates.io-index"
[source.xuanwu-sparse]
registry = "sparse+https://mirror.xuanwu.openatom.cn/index/"
[registries.xuanwu]
index = "https://mirror.xuanwu.openatom.cn/crates.io-index"
[net]
git-fetch-with-cli = true
"""
```

### 添加新源

要添加新的源，编辑 `config/sources.toml` 文件，在 `[sources]` 部分添加新的源配置：

```toml
[sources.新源名称]
rustup_dist_server = "https://your-mirror.com"
rustup_update_root = "https://your-mirror.com/rustup"
cargo_config = """
[source.crates-io]
replace-with = '新源名称'
[source.新源名称]
registry = "sparse+https://your-mirror.com/index/"
[net]
git-fetch-with-cli = true
"""
```

### 历史记录文件

每次切换源时，工具会更新 `config/history.toml` 历史记录文件。

历史记录文件内容示例：

```toml
[previous]
name = "xuanwu-sparse"
rustup_dist_server = "https://mirror.xuanwu.openatom.cn"
rustup_update_root = "https://mirror.xuanwu.openatom.cn/rustup"
cargo_config = "[source.crates-io]\nreplace-with = 'xuanwu-sparse'\n..."

[current]
name = "rsproxy-sparse"
rustup_dist_server = "https://rsproxy.cn"
rustup_update_root = "https://rsproxy.cn/rustup"
cargo_config = "[source.crates-io]\nreplace-with = 'rsproxy-sparse'\n..."
```

历史记录文件包含 `[previous]` 和 `[current]` 两个部分，每个部分都包含完整的源配置信息（源名称、环境变量和 Cargo 配置），方便追溯和回滚。

## 工作原理

1. **环境变量修改**：工具会修改 Windows 用户级环境变量：
   - `RUSTUP_DIST_SERVER`
   - `RUSTUP_UPDATE_ROOT`

2. **Cargo 配置**：工具会更新 `~/.cargo/config.toml` 文件（Windows 路径：`%USERPROFILE%\.cargo\config.toml`），完全覆盖文件内容。

3. **配置同步**：工具会更新 `config/sources.toml` 中的 `current` 字段，记录当前使用的源。

4. **历史记录**：每次切换都会生成历史记录文件，记录切换前后的源信息。

## 注意事项

1. **环境变量刷新**：修改 Windows 环境变量后，需要重启终端或重新打开命令行窗口才能生效。工具会尝试自动刷新，但某些情况下可能需要手动重启终端。

2. **Cargo 配置覆盖**：工具会完全覆盖 `~/.cargo/config.toml` 文件，如果该文件中有其他自定义配置，请先备份。

3. **管理员权限**：修改用户级环境变量不需要管理员权限，但如果需要修改系统级环境变量，需要以管理员身份运行。

4. **配置文件位置**：
   - 源配置文件：`config/sources.toml`（相对于脚本目录）
   - Cargo 配置文件：`~/.cargo/config.toml`（用户主目录）
   - 历史记录文件：`config/history.toml`（相对于脚本目录）

## 故障排查

### 问题：提示 "配置文件不存在"

**解决方案**：确保 `config/sources.toml` 文件存在。如果不存在，可以从示例配置创建。

### 问题：提示 "源 'xxx' 不存在"

**解决方案**：检查 `config/sources.toml` 文件中是否定义了该源，或者使用 `--list` 查看所有可用源。

### 问题：环境变量修改后不生效

**解决方案**：
1. 重启终端或命令行窗口
2. 如果安装了 Chocolatey，可以运行 `refreshenv` 命令
3. 检查环境变量是否已正确设置：`echo %RUSTUP_DIST_SERVER%`

### 问题：Cargo 配置不生效

**解决方案**：
1. 检查 `~/.cargo/config.toml` 文件是否存在且内容正确
2. 确认 Cargo 版本是否支持 sparse index（建议 >= 1.68）
3. 运行 `cargo --version` 检查 Cargo 版本

## 支持的镜像源

### rsproxy-sparse

- 官网：https://rsproxy.cn/
- 由字节跳动基础架构 Dev Infra 提供
- 支持 sparse index，速度更快

### xuanwu-sparse

- 官网：https://mirror.xuanwu.openatom.cn/
- 由玄武开源镜像站提供

## 许可证

本项目为工具脚本，可根据需要自由使用和修改。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。

## 更新日志

### v1.0.0
- 初始版本
- 支持多源切换
- 支持 Windows 环境变量自动配置
- 支持 Cargo 配置文件自动更新
- 支持历史记录功能
- 支持命令行参数覆盖


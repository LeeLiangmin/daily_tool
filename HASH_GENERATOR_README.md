# Hash 生成器工具

一个用于生成文件 hash 值的 Python 命令行工具，支持为单文件或目录中的所有文件生成 hash 值。生成的文件名格式为 `原文件名.算法`（如 `file.txt.sha256`），默认使用 sha256 算法，支持多种 hash 算法，并提供删除功能。

## 功能特性

- 🔐 **多算法支持**：支持 md5, sha1, sha224, sha256, sha384, sha512, blake2b, blake2s 等多种 hash 算法
- 📁 **目录处理**：支持单文件或目录（递归处理所有子目录）
- 🎯 **智能命名**：生成的文件名格式为 `原文件名.算法`（如 `file.txt.sha256`）
- 🚫 **忽略功能**：支持忽略指定的目录、子目录或文件（支持通配符）
- 🗑️ **批量删除**：支持删除目录下所有 hash 文件
- 💾 **大文件支持**：使用分块读取，支持处理大文件
- ✅ **错误处理**：完善的错误处理和用户友好的提示信息

## 安装

### 前置要求

- Python 3.6+
- 无需额外依赖（仅使用 Python 标准库）

### 安装方式

工具是独立的 Python 脚本，无需安装，直接使用即可：

```bash
# 直接运行
python hash_generator.py --help
```

## 使用方法

### 查看帮助

```bash
python hash_generator.py --help
```

### 基本用法

#### 为单个文件生成 hash

```bash
# 使用默认算法（sha256）为文件生成 hash
python hash_generator.py --file file.txt

# 或使用简写形式
python hash_generator.py -f file.txt

# 指定算法（如 md5）
python hash_generator.py --file file.txt --algorithm md5
python hash_generator.py -f file.txt -a md5
```

**输出示例：**
```
✓ 已生成: file.txt.sha256

✓ 成功生成 hash 文件
```

#### 为目录下所有文件生成 hash

```bash
# 递归处理目录下所有文件（默认）
python hash_generator.py --directory ./docs

# 或使用简写形式
python hash_generator.py -d ./docs

# 指定算法
python hash_generator.py --directory ./docs --algorithm md5

# 只处理当前目录，不递归子目录
python hash_generator.py --directory ./docs --no-recursive
```

**输出示例：**
```
✓ 已生成: docs\file1.txt.sha256
✓ 已生成: docs\file2.txt.sha256
✓ 已生成: docs\subdir\file3.txt.sha256

✓ 成功: 3 个文件
```

### 忽略功能

使用 `--ignore` 或 `-i` 参数可以忽略指定的目录、子目录或文件。支持通配符模式，可以多次使用来指定多个忽略规则。

#### 忽略单个目录

```bash
# 忽略 __pycache__ 目录
python hash_generator.py --directory ./docs --ignore "__pycache__"
```

#### 忽略多个目录和文件类型

```bash
# 忽略多个目录和文件类型
python hash_generator.py --directory ./docs \
    --ignore "*.pyc" \
    --ignore "__pycache__" \
    --ignore ".git" \
    --ignore "venv"

# 或使用简写形式
python hash_generator.py -d ./docs -i "*.pyc" -i "__pycache__" -i ".git"
```

#### 忽略模式示例

- `__pycache__` - 忽略所有名为 `__pycache__` 的目录
- `*.pyc` - 忽略所有 `.pyc` 文件
- `.git` - 忽略 `.git` 目录
- `venv` - 忽略 `venv` 目录
- `*.log` - 忽略所有 `.log` 文件
- `node_modules` - 忽略 `node_modules` 目录

### 删除功能

使用 `--delete` 参数可以删除目录下所有 hash 文件。

#### 删除单个 hash 文件

```bash
# 删除指定的 hash 文件
python hash_generator.py --file file.txt.sha256 --delete
```

#### 删除目录下所有 hash 文件

```bash
# 递归删除目录下所有 hash 文件
python hash_generator.py --directory ./docs --delete

# 只删除当前目录的 hash 文件，不递归
python hash_generator.py --directory ./docs --delete --no-recursive

# 删除时应用忽略规则
python hash_generator.py --directory ./docs --delete --ignore "venv"
```

**输出示例：**
```
✓ 已删除: docs\file1.txt.sha256
✓ 已删除: docs\file2.txt.sha256
✓ 已删除: docs\subdir\file3.txt.sha256

✓ 共删除 3 个 hash 文件
```

## 支持的算法

工具支持以下 hash 算法：

- `md5` - MD5 算法
- `sha1` - SHA-1 算法
- `sha224` - SHA-224 算法
- `sha256` - SHA-256 算法（默认）
- `sha384` - SHA-384 算法
- `sha512` - SHA-512 算法
- `blake2b` - BLAKE2b 算法
- `blake2s` - BLAKE2s 算法

### 指定算法

使用 `--algorithm` 或 `-a` 参数指定算法：

```bash
python hash_generator.py --file file.txt --algorithm md5
python hash_generator.py --file file.txt --algorithm sha512
python hash_generator.py --file file.txt --algorithm blake2b
```

## 文件命名规则

生成的 hash 文件命名格式：`原文件名.算法`

**示例：**
- `file.txt` → `file.txt.sha256`
- `image.png` → `image.png.md5`
- `document.pdf` → `document.pdf.sha512`

## 命令行参数

### 必需参数（二选一）

- `--file FILE, -f FILE` - 指定单个文件
- `--directory DIR, -d DIR` - 指定目录

### 可选参数

- `--algorithm ALG, -a ALG` - 指定 hash 算法（默认: sha256）
- `--delete` - 删除模式：删除所有 hash 文件
- `--recursive, -r` - 递归处理子目录（默认启用）
- `--no-recursive` - 不递归处理子目录
- `--ignore PATTERN, -i PATTERN` - 忽略指定的目录、子目录或文件（支持通配符，可多次使用）
- `--help, -h` - 显示帮助信息

## 使用场景

### 场景 1：为项目文件生成完整性校验

```bash
# 为项目所有文件生成 sha256 hash（忽略构建目录和缓存）
python hash_generator.py --directory ./project \
    --ignore "__pycache__" \
    --ignore "*.pyc" \
    --ignore "build" \
    --ignore "dist" \
    --ignore ".git"
```

### 场景 2：批量生成 MD5 校验文件

```bash
# 为下载目录的所有文件生成 MD5 校验文件
python hash_generator.py --directory ./downloads --algorithm md5
```

### 场景 3：清理所有 hash 文件

```bash
# 删除项目目录下所有 hash 文件
python hash_generator.py --directory ./project --delete
```

### 场景 4：为单个重要文件生成多种算法的 hash

```bash
# 生成 SHA256
python hash_generator.py --file important.zip --algorithm sha256

# 生成 SHA512
python hash_generator.py --file important.zip --algorithm sha512

# 生成 MD5
python hash_generator.py --file important.zip --algorithm md5
```

## 工作原理

1. **Hash 计算**：使用 Python 标准库 `hashlib` 进行 hash 计算
2. **文件读取**：使用分块读取（8KB 块），支持处理大文件而不会占用过多内存
3. **路径处理**：使用 `pathlib.Path` 进行跨平台路径处理
4. **忽略匹配**：使用 `fnmatch` 进行通配符模式匹配

## 注意事项

1. **Hash 文件覆盖**：如果目标 hash 文件已存在，工具会自动覆盖现有文件
2. **Hash 文件跳过**：工具会自动跳过 hash 文件本身（避免递归生成）
3. **大文件处理**：工具使用分块读取，可以处理任意大小的文件
4. **跨平台兼容**：工具在 Windows、Linux、macOS 上均可使用
5. **路径格式**：忽略模式支持通配符，路径分隔符会自动处理（`/` 和 `\`）

## 错误处理

工具提供完善的错误处理：

- **文件不存在**：提示警告并跳过
- **权限不足**：提示错误并跳过
- **无效算法**：提示错误并退出
- **目录为空**：正常处理，不报错

## 常见问题

### Q: 如何忽略多个目录？

A: 多次使用 `--ignore` 参数：

```bash
python hash_generator.py --directory ./docs \
    --ignore "venv" \
    --ignore "__pycache__" \
    --ignore ".git"
```

### Q: 如何只处理当前目录，不递归子目录？

A: 使用 `--no-recursive` 参数：

```bash
python hash_generator.py --directory ./docs --no-recursive
```

### Q: 生成的 hash 文件格式是什么？

A: Hash 文件是纯文本文件，内容为 hash 值的十六进制字符串，每行一个 hash 值。

### Q: 可以同时生成多种算法的 hash 文件吗？

A: 可以，多次运行命令指定不同算法即可：

```bash
python hash_generator.py --file file.txt --algorithm md5
python hash_generator.py --file file.txt --algorithm sha256
python hash_generator.py --file file.txt --algorithm sha512
```

### Q: 如何验证 hash 文件？

A: 可以使用其他工具（如 `sha256sum`、`md5sum`）验证，或使用本工具重新生成并比较。

## 示例输出

### 生成 hash 文件

```bash
$ python hash_generator.py --directory ./test --ignore "__pycache__"
✓ 已生成: test\file1.txt.sha256
✓ 已生成: test\file2.txt.sha256
✓ 已生成: test\subdir\file3.txt.sha256

✓ 成功: 3 个文件
```

### 删除 hash 文件

```bash
$ python hash_generator.py --directory ./test --delete
✓ 已删除: test\file1.txt.sha256
✓ 已删除: test\file2.txt.sha256
✓ 已删除: test\subdir\file3.txt.sha256

✓ 共删除 3 个 hash 文件
```

## 许可证

本项目为工具脚本，可根据需要自由使用和修改。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。

## 更新日志

### v1.1.0
- 添加忽略功能，支持忽略指定的目录、子目录或文件
- 支持通配符模式匹配
- 改进错误处理和用户提示

### v1.0.0
- 初始版本
- 支持单文件和目录处理
- 支持多种 hash 算法
- 支持递归处理子目录
- 支持删除 hash 文件功能
- 支持大文件处理


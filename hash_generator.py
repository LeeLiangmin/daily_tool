#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hash 生成器工具
支持为单文件或目录中的所有文件生成 hash 值
生成的文件名格式：原文件名.算法（如 file.txt.sha256）
"""

import os
import sys
import argparse
import hashlib
import fnmatch
from pathlib import Path
from typing import Set, Optional, List

# 支持的 hash 算法
SUPPORTED_ALGORITHMS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512,
    'blake2b': hashlib.blake2b,
    'blake2s': hashlib.blake2s,
}

# Hash 文件扩展名
HASH_EXTENSIONS = set(SUPPORTED_ALGORITHMS.keys())

# 默认算法
DEFAULT_ALGORITHM = 'sha256'

# 读取文件的块大小（用于大文件）
CHUNK_SIZE = 8192


def should_ignore(path: Path, ignore_patterns: List[str], base_path: Path) -> bool:
    """
    检查路径是否应该被忽略
    
    Args:
        path: 要检查的路径
        ignore_patterns: 忽略模式列表（支持通配符）
        base_path: 基础路径（用于计算相对路径）
        
    Returns:
        如果应该忽略返回 True，否则返回 False
    """
    if not ignore_patterns:
        return False
    
    # 计算相对路径（相对于 base_path）
    try:
        relative_path = path.relative_to(base_path)
    except ValueError:
        # 如果无法计算相对路径，使用绝对路径
        relative_path = path
    
    # 转换为字符串，使用正斜杠（跨平台兼容）
    path_str = str(relative_path).replace('\\', '/')
    path_parts = path_str.split('/')
    
    # 检查每个忽略模式
    for pattern in ignore_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue
        
        # 规范化模式（使用正斜杠）
        pattern = pattern.replace('\\', '/')
        
        # 检查完整路径是否匹配
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path_str, f"*/{pattern}"):
            return True
        
        # 检查路径的每个部分是否匹配
        for part in path_parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        
        # 检查路径是否以模式开头（用于目录）
        if path_str.startswith(pattern) or f"/{pattern}/" in path_str or path_str.endswith(f"/{pattern}"):
            return True
    
    return False


def calculate_hash(file_path: Path, algorithm: str) -> str:
    """
    计算单个文件的 hash 值
    
    Args:
        file_path: 文件路径
        algorithm: hash 算法名称
        
    Returns:
        hash 值的十六进制字符串
    """
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise ValueError(f"不支持的算法: {algorithm}")
    
    hash_func = SUPPORTED_ALGORITHMS[algorithm]()
    
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(CHUNK_SIZE):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except IOError as e:
        raise IOError(f"读取文件失败: {file_path} - {e}")


def is_hash_file(file_path: Path) -> bool:
    """
    判断文件是否为 hash 文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        如果是 hash 文件返回 True，否则返回 False
    """
    if not file_path.is_file():
        return False
    
    # 获取文件扩展名（去掉点号）
    suffix = file_path.suffix.lstrip('.')
    return suffix.lower() in HASH_EXTENSIONS


def generate_hash_file(file_path: Path, algorithm: str) -> Path:
    """
    为单个文件生成 hash 文件
    
    Args:
        file_path: 源文件路径
        algorithm: hash 算法名称
        
    Returns:
        生成的 hash 文件路径
    """
    # 计算 hash 值
    hash_value = calculate_hash(file_path, algorithm)
    
    # 生成 hash 文件路径：原文件名.算法
    hash_file_path = file_path.parent / f"{file_path.name}.{algorithm}"
    
    # 写入 hash 文件
    try:
        with open(hash_file_path, 'w', encoding='utf-8') as f:
            f.write(hash_value)
        return hash_file_path
    except IOError as e:
        raise IOError(f"写入 hash 文件失败: {hash_file_path} - {e}")


def process_file(file_path: Path, algorithm: str, ignore_patterns: Optional[List[str]] = None, base_path: Optional[Path] = None) -> bool:
    """
    处理单个文件（生成 hash）
    
    Args:
        file_path: 文件路径
        algorithm: hash 算法名称
        ignore_patterns: 忽略模式列表
        base_path: 基础路径（用于计算相对路径）
        
    Returns:
        成功返回 True，失败返回 False
    """
    # 跳过 hash 文件本身
    if is_hash_file(file_path):
        return False
    
    # 检查是否应该忽略
    if ignore_patterns and base_path:
        if should_ignore(file_path, ignore_patterns, base_path):
            return False
    
    # 检查文件是否存在
    if not file_path.is_file():
        print(f"⚠ 警告: 文件不存在，跳过: {file_path}")
        return False
    
    try:
        hash_file_path = generate_hash_file(file_path, algorithm)
        print(f"✓ 已生成: {hash_file_path}")
        return True
    except IOError as e:
        print(f"✗ 错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 未预期的错误: {file_path} - {e}")
        return False


def process_directory(directory_path: Path, algorithm: str, recursive: bool = True, ignore_patterns: Optional[List[str]] = None) -> tuple[int, int]:
    """
    处理目录（递归处理所有文件）
    
    Args:
        directory_path: 目录路径
        algorithm: hash 算法名称
        recursive: 是否递归处理子目录
        ignore_patterns: 忽略模式列表
        
    Returns:
        (成功数量, 失败数量)
    """
    if not directory_path.is_dir():
        print(f"✗ 错误: 目录不存在: {directory_path}")
        return (0, 0)
    
    success_count = 0
    fail_count = 0
    
    # 遍历目录
    if recursive:
        # 递归遍历所有文件和目录
        for item_path in directory_path.rglob('*'):
            # 检查目录是否应该被忽略
            if item_path.is_dir():
                if ignore_patterns and should_ignore(item_path, ignore_patterns, directory_path):
                    continue
            
            # 处理文件
            if item_path.is_file():
                if process_file(item_path, algorithm, ignore_patterns, directory_path):
                    success_count += 1
                else:
                    fail_count += 1
    else:
        # 只处理当前目录的文件
        for item_path in directory_path.iterdir():
            # 检查目录是否应该被忽略
            if item_path.is_dir():
                if ignore_patterns and should_ignore(item_path, ignore_patterns, directory_path):
                    continue
            
            # 处理文件
            if item_path.is_file():
                if process_file(item_path, algorithm, ignore_patterns, directory_path):
                    success_count += 1
                else:
                    fail_count += 1
    
    return (success_count, fail_count)


def delete_hash_files(directory_path: Path, recursive: bool = True, ignore_patterns: Optional[List[str]] = None) -> int:
    """
    删除目录下所有 hash 文件
    
    Args:
        directory_path: 目录路径
        recursive: 是否递归处理子目录
        ignore_patterns: 忽略模式列表
        
    Returns:
        删除的文件数量
    """
    if not directory_path.is_dir():
        print(f"✗ 错误: 目录不存在: {directory_path}")
        return 0
    
    deleted_count = 0
    
    # 遍历目录
    if recursive:
        # 递归遍历所有文件和目录
        for item_path in directory_path.rglob('*'):
            # 检查目录是否应该被忽略
            if item_path.is_dir():
                if ignore_patterns and should_ignore(item_path, ignore_patterns, directory_path):
                    continue
            
            # 处理 hash 文件
            if item_path.is_file() and is_hash_file(item_path):
                # 检查是否应该忽略
                if ignore_patterns and should_ignore(item_path, ignore_patterns, directory_path):
                    continue
                
                try:
                    item_path.unlink()
                    print(f"✓ 已删除: {item_path}")
                    deleted_count += 1
                except IOError as e:
                    print(f"✗ 删除失败: {item_path} - {e}")
                except Exception as e:
                    print(f"✗ 未预期的错误: {item_path} - {e}")
    else:
        # 只处理当前目录的文件
        for item_path in directory_path.iterdir():
            # 检查目录是否应该被忽略
            if item_path.is_dir():
                if ignore_patterns and should_ignore(item_path, ignore_patterns, directory_path):
                    continue
            
            # 处理 hash 文件
            if item_path.is_file() and is_hash_file(item_path):
                # 检查是否应该忽略
                if ignore_patterns and should_ignore(item_path, ignore_patterns, directory_path):
                    continue
                
                try:
                    item_path.unlink()
                    print(f"✓ 已删除: {item_path}")
                    deleted_count += 1
                except IOError as e:
                    print(f"✗ 删除失败: {item_path} - {e}")
                except Exception as e:
                    print(f"✗ 未预期的错误: {item_path} - {e}")
    
    return deleted_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Hash 生成器工具 - 为文件或目录生成 hash 值',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支持的算法: {', '.join(SUPPORTED_ALGORITHMS.keys())}
默认算法: {DEFAULT_ALGORITHM}

示例:
  python hash_generator.py --file file.txt                    # 为单个文件生成 sha256 hash
  python hash_generator.py --file file.txt --algorithm md5   # 为单个文件生成 md5 hash
  python hash_generator.py --directory ./docs                # 为目录下所有文件生成 sha256 hash（递归）
  python hash_generator.py --directory ./docs --algorithm md5 # 为目录下所有文件生成 md5 hash（递归）
  python hash_generator.py --directory ./docs --delete       # 删除目录下所有 hash 文件（递归）
  python hash_generator.py --directory ./docs --no-recursive # 只处理当前目录，不递归
  python hash_generator.py --directory ./docs --ignore "*.pyc" --ignore "__pycache__"  # 忽略指定文件/目录
  python hash_generator.py --directory ./docs --ignore ".git" --ignore "venv"  # 忽略多个目录
        """
    )
    
    # 文件或目录参数（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--file',
        '-f',
        metavar='FILE',
        type=str,
        help='指定单个文件'
    )
    group.add_argument(
        '--directory',
        '-d',
        metavar='DIR',
        type=str,
        help='指定目录'
    )
    
    # 算法参数
    parser.add_argument(
        '--algorithm',
        '-a',
        metavar='ALG',
        type=str,
        default=DEFAULT_ALGORITHM,
        help=f'指定 hash 算法（默认: {DEFAULT_ALGORITHM}）'
    )
    
    # 删除模式
    parser.add_argument(
        '--delete',
        action='store_true',
        help='删除模式：删除所有 hash 文件'
    )
    
    # 递归选项
    parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        default=True,
        help='递归处理子目录（默认启用）'
    )
    parser.add_argument(
        '--no-recursive',
        dest='recursive',
        action='store_false',
        help='不递归处理子目录'
    )
    
    # 忽略选项
    parser.add_argument(
        '--ignore',
        '-i',
        metavar='PATTERN',
        action='append',
        dest='ignore_patterns',
        help='忽略指定的目录、子目录或文件（支持通配符，可多次使用）。例如: --ignore "*.pyc" --ignore "__pycache__" --ignore ".git"'
    )
    
    args = parser.parse_args()
    
    # 验证算法
    if args.algorithm.lower() not in SUPPORTED_ALGORITHMS:
        print(f"✗ 错误: 不支持的算法: {args.algorithm}")
        print(f"支持的算法: {', '.join(SUPPORTED_ALGORITHMS.keys())}")
        sys.exit(1)
    
    algorithm = args.algorithm.lower()
    
    try:
        if args.delete:
            # 删除模式
            if args.file:
                file_path = Path(args.file)
                if is_hash_file(file_path):
                    try:
                        file_path.unlink()
                        print(f"✓ 已删除: {file_path}")
                    except Exception as e:
                        print(f"✗ 删除失败: {file_path} - {e}")
                        sys.exit(1)
                else:
                    print(f"✗ 错误: 文件不是 hash 文件: {file_path}")
                    sys.exit(1)
            elif args.directory:
                directory_path = Path(args.directory)
                deleted_count = delete_hash_files(directory_path, args.recursive, args.ignore_patterns)
                print(f"\n✓ 共删除 {deleted_count} 个 hash 文件")
        else:
            # 生成模式
            if args.file:
                file_path = Path(args.file)
                if process_file(file_path, algorithm):
                    print(f"\n✓ 成功生成 hash 文件")
                else:
                    print(f"\n✗ 生成 hash 文件失败")
                    sys.exit(1)
            elif args.directory:
                directory_path = Path(args.directory)
                success_count, fail_count = process_directory(directory_path, algorithm, args.recursive, args.ignore_patterns)
                print(f"\n✓ 成功: {success_count} 个文件")
                if fail_count > 0:
                    print(f"✗ 失败: {fail_count} 个文件")
    
    except KeyboardInterrupt:
        print("\n\n已取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


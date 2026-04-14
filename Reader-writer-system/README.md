# 操作系统读写系统 - 读者优先模型

本项目实现了操作系统中的经典同步问题——读者-写者问题（Readers-Writers Problem），采用读者优先（Reader-First）策略解决并发访问共享数据的同步与互斥问题。

## 项目概述

读者-写者问题是操作系统中的经典同步问题：多个线程可以同时读取共享数据，但写入时需要独占访问。本项目实现了读者优先策略，即当有读者在读取时，写者必须等待所有读者完成才能写入；同时新的读者可以随时加入读取。

## 项目结构

```
Reader-writer-system/
├── readerfirst/
│   ├── readers_writers/
│   │   ├── reader_writer-1.c    # 读者优先实现 v1
│   │   └── reader_writer-2.c     # 读者优先实现 v2（改进版）
│   └── performance_analysis/
│       ├── PERFORMANCE_ANALYSIS.md    # 性能分析报告
│       └── *.png/*.csv              # 实验数据与图表
├── performance_analysis_reader_first.png
├── performance_analysis_reader_first.pdf
└── performance_results_reader_first.csv
```

## 技术实现

### 同步机制
- **互斥锁 (pthread_mutex_t)**: 保护共享变量的原子访问
- **条件变量 (pthread_cond_t)**: 实现线程间的同步与唤醒

### 核心变量
```c
int data = 0;          // 共享数据
int read_count = 0;   // 当前活跃的读者数量
int writer_active = 0; // 是否有写者正在占用
```

### 读者逻辑
1. 获取互斥锁
2. 检查是否有写者活跃，如有则等待
3. 增加读者计数，进入临界区读取
4. 读取完成后减少读者计数
5. 如果没有读者了，唤醒等待的写者

### 写者逻辑
1. 获取互斥锁
2. 检查是否有其他写者或读者活跃，如有则等待
3. 设置 writer_active 为 1，进入临界区写入
4. 写入完成后唤醒所有等待线程

## 编译与运行

### 编译

```bash
gcc reader_writer-1.c -o rw -pthread
gcc reader_writer-2.c -o rw_test -pthread
```

### 运行

```bash
./rw        # 运行 5 秒后自动结束
./rw_test  # 运行 5 秒后正常退出
```

## 性能分析

详细的性能分析请参见 [PERFORMANCE_ANALYSIS.md](readerfirst/PERFORMANCE_ANALYSIS.md)。

### 主要发现

| 配置 | 读操作/s | 写操作/s | 特点 |
|------|----------|----------|------|
| 10:1 | 28.32 | 43.32 | 读多写少，性能优异 |
| 3:3 | 1.67 | 146.90 | 读写平衡，写者占优 |
| 1:5 | 0.33 | 257.89 | 写多读少，读者饿死 |

### 结论

- **读者优先策略适合读多写少的场景**（如搜索引擎、缓存系统）
- **在高写者比例场景下会出现读者饥饿问题**
- 选择同步策略需根据实际业务读写比例决定

## 文件说明

| 文件 | 说明 |
|------|------|
| reader_writer-1.c | 基础实现，使用 pthread_cancel 终止线程 |
| reader_writer-2.c | 改进实现，使用 flag 优雅退出 |
| PERFORMANCE_ANALYSIS.md | 详细性能分析报告 |
| performance_results_*.csv | 实验测试数据 |

## 依赖环境

- Linux/macOS 或 Windows (MinGW/MSYS2)
- GCC 编译器
- POSIX Threads (pthread)

## 作者

操作系统课程项目 - 2026年4月
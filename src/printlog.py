import sys
import os


def printlog(a, b):
    res = a + b
    print(res)
    # Open the file in write mode
    with open('log.text', 'w') as file:
        # Write the result to the file
        file.write(f"Result of {a} + {b} = {res}\n")


if __name__ == '__main__':

    print(sys.argv)
    # 从命令行获取参数
    args = sys.argv[1:]  # 跳过第一个参数，因为它是脚本的名称

    # 检查参数是否正确
    if len(args) != 2:
        print("Usage: python printlog.py <arg1> <arg2>")
        sys.exit(1)  # 退出程序，返回非零状态码表示错误
        # 将参数传递给 printlog 函数
    printlog(args[0], args[1])

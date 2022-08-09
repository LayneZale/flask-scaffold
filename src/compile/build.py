#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: luyang.ying
@Contact: luyang.ying@hongpucorp.com
@File name: build.py
@Create time: 2022/3/28 16:01
@Desc: 
"""

import os
import sys
import yaml
import shutil
import logging
import subprocess
import logging.handlers


class Log:
    @staticmethod
    def init():
        """初始化日志模块"""
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                            filename='compile.log',
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


class Build:
    def __init__(self):
        # 读取配置yml
        self.__env_path = os.path.join(os.getcwd(), '../compile.yml')
        self.__root_path = sys.path[0]
        with open(self.__env_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        env = yaml.load(file_content, yaml.FullLoader)

        self.__init_path = env.get('compile_path')  # 编译根路径
        self.__include_module_name_list = env.get('include_module_name_list')  # 需要编译的模块名称(容器根目录下)
        self.__exclude_file_name_list = env.get('exclude_file_name_list')  # 排除的文件名称列表
        self.__exclude_folder_name_list = env.get('exclude_folder_name_list')  # 排除的文件夹名称列表
        self.__need_clean_file_folder_path_list = env.get('need_clean_file_folder_path_list')  # 额外需要删除的文件(容器根目录相对路径)

        os.chdir(os.getcwd())  # 进入脚本路径位置
        self.__build_path = os.path.abspath(self.__init_path)
        os.chdir(self.__build_path)  # 进入需要编译的文件夹位置

        self.__need_delete_suffix_name_list = ['.pyi', '.py']

    def __compile_file(self, file: str) -> (int, str):
        """
        编译文件
        :return 0: 编译完成
        :return 1: 编译失败
        """
        if sys.platform == 'linux':
            cmd = 'python3 -m nuitka --module {}'.format(file)
        else:
            cmd = 'python -m nuitka --module {}'.format(file)
        code, result = subprocess.getstatusoutput(cmd)
        if code == 0:
            # 删除构建文件夹
            file_prefix = os.path.splitext(file)[0]
            self.__delete_folder('{}.compile'.format(file_prefix))
            for need_delete_suffix_name in self.__need_delete_suffix_name_list:
                self.__delete_file('{}{}'.format(file_prefix, need_delete_suffix_name))
        return code, result

    def __compile_folder(self, folder: str) -> (int, str):
        """
        编译文件夹
        :return 0: 编译完成
        :return 1: 编译失败
        """
        if sys.platform == 'linux':
            cmd = 'python3 -m nuitka --module --include-module={} {}'.format(folder, folder)
        else:
            cmd = 'python -m nuitka --module --include-module={} {}'.format(folder, folder)
        code, result = subprocess.getstatusoutput(cmd)
        if code == 0:
            # 删除构建文件夹
            self.__delete_folder('{}.compile'.format(folder))
            self.__delete_folder(folder)
            self.__delete_file('{}.pyi'.format(folder))
        return code, result

    @staticmethod
    def __delete_folder(folder_path: str):
        """删除文件夹"""
        # noinspection PyBroadException
        try:
            shutil.rmtree(folder_path)
        except:
            pass

    @staticmethod
    def __delete_file(file_path: str):
        """删除文件"""
        # noinspection PyBroadException
        try:
            os.remove(file_path)
        except:
            pass

    def __walk_dir(self, path: str):
        """递归路径"""
        logging.info('当前路径: {}'.format(path))
        os.chdir(path)

        # 删除多余文件夹
        self.__delete_folder('__pycache__')
        self.__delete_folder('.idea')
        self.__delete_folder('.vscode')
        self.__delete_folder('.github')

        # 开始递归编译
        file_rel_path_list = os.listdir()
        for file_rel_path in file_rel_path_list:
            os.chdir(path)
            if os.path.isdir(file_rel_path):  # 如果是文件夹
                self.__find_folder(base_path=path, folder_name=file_rel_path)
            else:  # 如果是文件
                self.__find_file(base_path=path, file_name=file_rel_path)

    def run(self):
        """运行"""
        logging.info('当前路径: {}'.format(self.__build_path))
        os.chdir(self.__build_path)

        # 删除多余文件夹
        self.__delete_folder('__pycache__')
        self.__delete_folder('.idea')
        self.__delete_folder('.vscode')
        self.__delete_folder('.github')

        # 编译文件夹模块
        for need_compile_module_name in self.__include_module_name_list:
            if os.path.isdir(need_compile_module_name):  # 如果是文件夹
                os.chdir(self.__build_path)
                logging.info('正在编译模块 {}'.format(need_compile_module_name))
                code, result = self.__compile_folder(need_compile_module_name)
                if code == 0:  # 编译完成
                    logging.info('编译模块 {} 完成'.format(need_compile_module_name))
                else:
                    logging.warning('编译模块 {} 失败, 过程: {}'.format(need_compile_module_name, result))
            else:
                logging.error('模块 {} 不是文件夹'.format(need_compile_module_name))

        # 编译其余文件
        self.__walk_dir(self.__build_path)

    def __find_folder(self, base_path: str, folder_name: str):
        """发现文件夹"""
        folder_path = os.path.join(base_path, folder_name)
        if folder_name not in self.__exclude_folder_name_list:
            logging.info('进入 {} 文件夹'.format(folder_path))
            self.__walk_dir(folder_path)
        else:
            logging.info('忽略文件夹: {}'.format(folder_path))

    def __find_file(self, base_path: str, file_name: str):
        """发现文件"""
        file_path = os.path.join(base_path, file_name)

        if file_name not in self.__exclude_file_name_list and os.path.splitext(file_name)[-1] == '.py':
            logging.info('正在编译文件 {}'.format(file_name))
            code, result = self.__compile_file(file_name)
            if code == 0:  # 编译完成
                logging.info('编译 {} 完成'.format(file_name))
            else:
                logging.warning('编译失败: 文件: {}, 过程: {}'.format(file_path, result))
        else:
            logging.info('忽略文件: {}'.format(file_name))

    def clean(self):
        """清理文件"""
        os.chdir(self.__build_path)
        self.__delete_file(self.__env_path)  # 清理配置yml
        self.__delete_folder(self.__root_path)  # 清理自身

        # 删除额外文件和文件夹
        for need_clean_file_folder_path in self.__need_clean_file_folder_path_list:
            if os.path.exists(need_clean_file_folder_path):
                if os.path.isdir(need_clean_file_folder_path):  # 如果是文件夹
                    self.__delete_folder(need_clean_file_folder_path)
                    logging.info('成功删除文件夹 {}'.format(need_clean_file_folder_path))
                else:  # 如果是文件
                    self.__delete_file(need_clean_file_folder_path)
                    logging.info('成功删除文件 {}'.format(need_clean_file_folder_path))
            else:
                logging.error('路径 {} 不存在'.format(need_clean_file_folder_path))

        logging.info('清理完成')


if __name__ == '__main__':
    Log.init()
    build = Build()
    build.run()
    build.clean()

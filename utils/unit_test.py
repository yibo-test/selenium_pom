import os
import unittest
from utils.common import get_path_last_name, find_file_path


def generate_unittest_suite(testcase_ids: list, testcase_start_dir="test_cases"):
    """
    把testcase_ids中的用例加载到测试套中
    :param testcase_ids: 用例集，list类型,用例id的格式为 module[.class[.method]]，中括号中缺省
    :param testcase_start_dir: 测试用例的根目录，指的是项目目录下用例所在的目录
    :return: 返回测试套
    """
    # 将用户输入的用例目录转换成绝对路径
    testcase_start_dir_abspath = os.path.abspath(testcase_start_dir)

    # 获取用例根目录的名称
    testcase_dir_name = get_path_last_name(testcase_start_dir_abspath)

    if not isinstance(testcase_ids, list):
        raise ValueError(f"参数{testcase_ids}不是list类型")

    if not os.path.exists(testcase_start_dir_abspath):
        raise ValueError(f"用例根目录 {testcase_dir_name} 在目录{os.getcwd()}中不存在，请修改用例根目录")

    # 根据用例id，获取所有用例的模块名称
    exist_file_modules = []
    not_exist_file_module = []
    for testcase_id in testcase_ids:
        filename = testcase_id.split(".")[0]

        # 根据模块名，查找文件，若不存在则反None
        file_path = find_file_path(testcase_start_dir_abspath, filename)
        if file_path:
            exist_file_modules.append(filename)
        else:
            not_exist_file_module.append(filename)

    # 校验是否存在没有用例文件的模块
    if not_exist_file_module:
        raise ValueError(f"这些用例模块{not_exist_file_module}不存在用例文件，请核实！")

    # 注册文件为用例目录下__init__.py文件
    register_file = rf"{testcase_start_dir_abspath}\__init__.py"

    # 校验注册文件存不存在
    if not os.path.exists(register_file):
        # 不存在就创建
        with open(register_file, "w") as f:
            pass

    # 获取已注册的用例模块
    import_module_names = []
    with open(register_file, "r") as f:
        for line in f.read().splitlines():
            name = line.split(" ")[-1]
            import_module_names.append(name)

    # 对列表进行排序，并校验两个列表是否相等
    exist_file_modules.sort()
    import_module_names.sort()
    if exist_file_modules != import_module_names:
        # 当前执行文件所在的目录名称
        project_path = get_path_last_name()

        # 如果不一致，找出未注册用例模块，并自动注册
        for file_module in exist_file_modules:
            if file_module not in import_module_names:
                # 通过用例模块找到文件路径
                file_path = find_file_path(testcase_start_dir_abspath, file_module)
                file_path = file_path.split(project_path)[-1]

                # 从文件路径提取目录路径
                split_path = file_path.split(".")[0].split("\\")
                split_path.remove(file_module)
                split_path.remove("")

                # 拼接注册信息
                file_module_path = ".".join(split_path)
                register_msg = f"from {file_module_path} import {file_module}\n"

                # 注册用例模块
                with open(register_file, "a") as f:
                    f.write(register_msg)

    # 将所有用例加载到测试套中
    suite = unittest.TestSuite()
    for testcase_id in testcase_ids:
        testcase_id = f"{testcase_dir_name}.{testcase_id}"
        suite.addTest(unittest.TestLoader().loadTestsFromName(testcase_id))
    return suite
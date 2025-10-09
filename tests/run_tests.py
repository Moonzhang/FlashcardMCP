import unittest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所有测试模块
from tests import test_json_validator
from tests import test_markdown_parser
from tests import test_card_generator


def run_all_tests():
    """运行所有测试并输出结果"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加各个测试模块到测试套件 - 修复makeSuite错误
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_json_validator.TestJsonValidator))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_markdown_parser.TestMarkdownParser))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_card_generator.TestCardGenerator))
    
    # 运行测试并显示结果
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试是否全部通过
    return result.wasSuccessful()


def run_individual_test(test_module_name):
    """运行单个测试模块"""
    # 测试模块映射
    test_modules = {
        'json': test_json_validator.TestJsonValidator,
        'markdown': test_markdown_parser.TestMarkdownParser,
        'card': test_card_generator.TestCardGenerator
    }
    
    # 检查测试模块是否存在
    if test_module_name not in test_modules:
        print(f"错误: 找不到测试模块 '{test_module_name}'")
        print("可用的测试模块:")
        for module in test_modules.keys():
            print(f"  - {module}")
        return False
    
    # 创建测试套件并运行 - 修复makeSuite错误
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_modules[test_module_name]))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 运行指定的测试模块
        success = run_individual_test(sys.argv[1])
    else:
        # 运行所有测试
        print("运行所有测试...")
        success = run_all_tests()
    
    # 根据测试结果设置退出码
sys.exit(0 if success else 1)
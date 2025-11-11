import pytest
import random
from collections import defaultdict

# Счетчики для каждого assert
assert_stats = defaultdict(lambda: {'passed': 0, 'failed': 0, 'total': 0})


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Перехватываем результаты выполнения тестов"""
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call' and report.failed:
        # Анализируем traceback для подсчета проваленных assert'ов
        if report.longrepr:
            traceback = str(report.longrepr)
            # Считаем количество AssertionError в traceback
            assertion_errors = traceback.count('AssertionError')
            test_name = item.nodeid.split('::')[-1]
            assert_stats[test_name]['failed'] += assertion_errors
            assert_stats[test_name]['total'] += assertion_errors


def pytest_runtest_call(item):
    """Перехватываем вызов теста для подсчета assert'ов"""
    # Получаем исходный код тестовой функции
    try:
        import inspect
        test_function = item.function
        source_code = inspect.getsource(test_function)

        # Считаем количество assert в коде теста
        assert_count = source_code.count('assert ')
        test_name = item.nodeid.split('::')[-1]

        # Инициализируем счетчик для этого теста
        if test_name not in assert_stats:
            assert_stats[test_name] = {'passed': 0, 'failed': 0, 'total': 0}

        assert_stats[test_name]['total'] = assert_count
        assert_stats[test_name]['passed'] = assert_count  # Предполагаем, что все пройдут

    except:
        pass


def pytest_sessionfinish(session, exitstatus):
    """Вывод статистики по assert'ам"""
    print("\n\n" + "=" * 70)
    print("СТАТИСТИКА ПО ASSERT'АМ")
    print("=" * 70)

    total_asserts = 0
    total_passed = 0
    total_failed = 0

    for test_name, stats in sorted(assert_stats.items()):
        if stats['total'] > 0:
            # Корректируем passed: total - failed
            stats['passed'] = stats['total'] - stats['failed']

            total_asserts += stats['total']
            total_passed += stats['passed']
            total_failed += stats['failed']

            success_rate = (stats['passed'] / stats['total']) * 100
            print(
                f"{test_name:20} | Asserts: {stats['total']:5} | ✓: {stats['passed']:5} | ✗: {stats['failed']:5} | {success_rate:5.1f}%")

    print("-" * 70)
    if total_asserts > 0:
        overall_success = (total_passed / total_asserts) * 100
        print(
            f"{'ИТОГО':20} | Asserts: {total_asserts:5} | ✓: {total_passed:5} | ✗: {total_failed:5} | {overall_success:5.1f}%")
    print("=" * 70)


@pytest.fixture
def random_numbers():
    def _random_numbers(count=10, max_value=999999999999):
        return [random.randint(0, max_value) for _ in range(count)]

    return _random_numbers


@pytest.fixture
def all_genders():
    return ["М", "Ж", "С"]


@pytest.fixture
def all_cases():
    return ["И", "Р", "Д", "В", "Т", "П"]
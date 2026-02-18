import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="endstone-easyhotpotato",
    version="0.1.0",
    author="MengHanLOVE",
    url='https://github.com/MengHanLOVE1027',
    author_email="2193438288@qq.com",
    description="基于 EndStone 的最最最简单的Python热土豆插件 / The simplest Python hot potato plugin based on EndStone.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)

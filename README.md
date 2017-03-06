# xmind2testlink

With this tool, you will be able to convert [xmind](https://www.xmind.net/) tests to [testlink](http://www.testlink.org/) tests xml files. You should have python installed before running it.

## Design test cases via [xmind](https://www.xmind.net/)

Xmind is an excellent mindmap tool, which can help you design test cases easily.  To create a ***convertible*** xmind, please design your test cases like this:

![test_case_by_xmind](doc/test_case_by_xmind.png)

**Guidelines & Rules:**

1. `Notes` for a test suite will be converted to `details` in TestLink.
2. `Notes` for a test case will be converted to `summary` in TestLink.
3. `Comments` for a test case will be converted to `preconditions` in TestLink.
4. `Priority` maker for a test case will be converted to `importance` in TestLink.
5. Sub topics for a test case will be treated as test steps.
   - It is okay to design test step **with action** but **without expected results**.
6. Use `!` to ignore any test suite / test case / test step that you don't want to convert.
7. The root topic will not be converted, please treat it as target suite node in TestLink.
8. Free topic and notes will not be converted.
9. Only the mindmap in first sheet will be converted.

Download the sample xmind file: [test_case_by_xmind](doc/test_case_by_xmind.xmind)

## Generate the TestLink xml file

Once your xmind had been created, use bellow command to convert it to TestLink recognized xml file.

```shell
cd src
python xmind2testlink.py /path/to/testcase.xmind
```

An xml with same name will be generated in your xmind directory.

## Import the xml into TestLink

Go to your TestLink website, import the xml into your target test suite step by step.

![testlink_import_1](doc/testlink_import_1.png)

To avoid duplicates, you might want to *Update date on Latest version*.

![testlink_import_2](doc/testlink_import_2.png)

Once you click on the **Upload file** button, all the tests will be imported as they listed in xmind.

![testlink_import_3](doc/testlink_import_3.png)

The field mapping looks like below figure.

![testlink_import_4](doc/testlink_import_4.png)

## Advanced usage

A simple webpage to host this feature also has been built in  `web` folder. To starting the website, here is the command:

```shell
cd web
python application.py
```

Start a browser, then you will be able to convert xmind to TestLink via http://127.0.0.1:5000. I am not good at web design, but I am trying my best to provide a friendly interface :(-)

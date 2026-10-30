---
name: principle-test-behavior-not-implementation
description: "写、改或保留一条测试时读。按用户的方式调用并断言精确结果；导入的函数全返回 undefined 还能过的测试，重写或删。"
disable-model-invocation: true
---

# Test behavior, not implementation

写、改或保留一条测试时读。

## 判据

测试像用户那样调用被测代码，断言它给出的精确结果。导入的函数全返回 `undefined` 或错值，这条测试还能过，就要重写或删。

这几种形状过不了这一关：

- 松断言或不断言：`toBeDefined`、`toBeTruthy`、`not.toThrow`、`toBeGreaterThan(0)`。
- 只断调用发生或没发生：`toHaveBeenCalled`、`not.toHaveBeenCalled`、`toBeUndefined`、`toEqual([])`。
- 期望值由被测代码自己算：`expect(f(a)).toBe(f(a))`。
- 复述常量、配置默认值、表格行或提示词原文。
- 只断言测试自己捏的数据，没有调用被测对象。

改法：测试体里用一组具体输入调用被测对象，断言字面输出或副作用。有 mock 的，断言它收到的负载。要断言"没有"的，在另一个输入上同时断言"有"。要测常量，用一组输入测读它的那段机制，不要复述值。

这些留下：跨表格行的关系检查（一个键在两张表里、父记录存在），和 `*.test-d.ts` 这类类型检查。

## 收工

- 回复里点名这次涉及哪几条测试，各自属于上面哪种形状，或者为什么不属于。
- 删掉一条测试时说明它原来能盖住什么，以及那件事现在由哪条测试或哪个检查盖住。

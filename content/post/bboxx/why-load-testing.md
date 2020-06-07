---
title: Why is load testing important?
date: 2018-06-13
tags: ["bboxx", "testing", "tech"]
---

Testing is an essential part of *all* product development.
It's likely everything you can see right now has been extensively tested at some point.
Testing for software development is just as important than testing any other product,
but is often back-benched since it isn't explicitly productive. Would you ever use an
appliance that has *never* been tested? Drive a car?

Like it or not, if you ever want anybody to use your code with confidence, you need to write tests.

### Unit Testing

Unit testing is writing test cases that test specific components of the code for properties that
it should have. For example, an `Add` component could have the following tests:

```Python
assert(Add(1, 2) == 3)    # Simple addition of two numbers
assert(Add(1, -2) == -1)  # Positive + negative
assert(Add(-1, -1) == -2) # Negative + negative
assert(Add(1, 0) == 1)    # 1 + 0 = 1
```

Writing tests for components like this, however basic the tests are, is always useful
for detecting when things break. If you have some sort of
[continuous integration](https://www.atlassian.com/continuous-delivery/continuous-integration-intro),
it will immediately become obvious if a seemingly innocuous change to your codebase
has inadvertently broken some core functionality of your code.

However, unit testing relies on the developer having the foresight to think of all possible edge cases,
and for user-facing software, all possible uses and states that the system can be in. Clearly, this is
impossible in most cases.

### Property-based Testing

Property-based testing, or randomised testing, is a testing methodology that was popularised
by the functional programming paradigm and languages like Haskell and F#, but has started to
take hold in other languages[^1].

It involves stating properties that should always hold true,
and then randomising the input data in an attempt to cover all possible inputs,
so that you know whatever comes into your program, the properties will hold.

Example properties for our `Add` component could be the following:
```Python
assert(Add(x,0) == x)          # Adding zero to any x is equal to x.
assert(Add(Add(x,-1), 1) == x) # Adding -1 then +1 to any x will result in x.
```

In this case, with such a trivial component, the examples are more to illustrate the concept rather
than the usefulness of property-based testing, since for Addition it's possible for a conscientous
developer to think of all edge cases.

Testing all possible combinations is called exhaustive testing.
Normally, for complex problems, exhaustive testing is impossible
so random testing is as good as it gets.

<div class="well">

#### Randomised Testing Statistics ^[Taught by [Dr Tom Clarke](https://www.imperial.ac.uk/people/t.clarke) at Imperial College London.]

If your input data has \\(n\\) possible distinct combinations and you conduct \\(r\\)
random tests what are the chances that you cover all combinations? The chance that
any one combination is not covered is \\( (1-1/n)^r \\).

This is true, independently, for all \\(n\\) combinations,
so the chance of complete coverage is
\\( (1 - (1- 1/n)^r)^n \\).

Using the approximation
\\( (1-\varepsilon)^n \approx e^{-n\varepsilon} \\) twice,
this simplifies to
\\( e^{-n(e^{-r/n})} \approx 1-ne^{-r/n} \\).

So for \\(r=Kn+log_e n\\) this becomes very close to \\( 1-e^{-K}\\).
The penalty in required extra tests using random testing instead of
exhaustive testing is thus not very large and \\(10\times\\) the
number of tests \\((K=10)\\) will suffice to make random testing
almost certainly as good as exhaustive testing.

\\((K=8)\\) gives \\(6\sigma\\) (6 standard deviation) confidence that all combinations have been checked.
</div class="well">
<span name='process-testing' id='process-testing' class='anchor'></span>
For more on property-based testing (written in relation to F# but very clearly explained), read [this](https://fsharpforfunandprofit.com/posts/property-based-testing/) by [ScottW](https://fsharpforfunandprofit.com/about/). 

<!-- https://pixelflips.com/blog/anchor-links-with-a-fixed-header -->

### Automated process testing

Process testing is a term I've coined for the sake of this post.
It describes tests that encompass the whole of a user process.
For example, you may have unit tests for `log in`, `add to basket`,
and `checkout`, but no test for the process as a whole. Usually,
there should be several predefined user workflows which are
already clearly specified from the design stages, so it is
easy to know which mission critical processes need to have
these tests. 

If a deploy of code breaks one of these workflows, it would interrupt
a core business process, so there should be automated tests to
ensure that this is not happening.

However, sometimes these sorts of tests are done interactively;
code will be unit-tested, tested interactively on a test server
then merged and unit-tested again by CI (Continuous Integration).

There should be some measure of business critical process testing
(could be called a form of unit test, since you are testing a process as a component),
as well as unit tests.

### Load testing

Property-based testing helps to find edge cases to include in your unit tests
(these can take time so perhaps can be run semi-regularly but not every push). 

Automated unit and process tests provide assurance that any new changes aren't
breaking existing functionality as far as you *can* know, and are usually fast
enough that they should be run on or before every commit.

What these tests miss:

- If your changes break when used concurrently[^2]
- If your changes add too much latency.
- If your changes are too computationally or storage heavy.

When testing just one user, all these problems are invisible.

Wouldn't you liked to have known 6 months ago the crucial fix
you deployed was unscalable and would slow your whole system
down to a crawl 6 months later? Or know the true cost of running
your system for X users before selling off your SAAS at a loss.

This is the importance of load testing, and the inspiration for
[Project Mystic](/post/bboxx/project-mystic), a project to develop a framework
for *Process Load Testing*, which is load testing which maps out
the processes that need to be tested and simulates a more realistic
fulfilment of processes than simple endpoint spamming.

[^2]:
    When a function is used at the same time as the same or a different function.

### References

[^1]: 
    Some property-based testing resources for popular programming languages:

    |Language|Resource|
    |--------|--------|
    |   F#   | [FsCheck](https://fscheck.github.io/FsCheck/)
    | Haskell| [QuickCheck](https://hackage.haskell.org/package/QuickCheck)
    | OCaml  | [qCheck](https://github.com/c-cube/qcheck)
    | Python | [Hypthesis](https://hypothesis.readthedocs.io/en/latest/)
    | Kotlin | [KotlinTest](https://github.com/kotlintest/kotlintest)
    | Java   | [QuickTheories](https://github.com/ncredinburgh/QuickTheories)
    | C++    | [RapidCheck](https://github.com/emil-e/rapidcheck)
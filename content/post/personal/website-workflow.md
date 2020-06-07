---
title: Website Serverless Architecture
subtitle: Designing a workflow for deploying
date: 2018-06-13
tags: ["website", "hugo", "serverless"]
draft: true
---

Recently I've developed an interest in the so-called 'serverless' architectures which are the current trend in the tech world today.
I attended a talk recently at the AWS London Summit 2018 by River Island on their migration to a cloud-based infrastructure.
They made extensive use of Lambda functions, and running their ORM now costs fractions of what it once did.

A project at work will be to investigate possible uses for this technology, and to develop guidelines for developing for this
kind of architecture. Hence it was a serendipitous opportunity to deploy my own website using these technologies and kill
two birds with one stone; learn about serverless infrastructure, and deploy my website on a cheap, pay-per-hit service.

The workflow so far that I've designed is based on [How to host Hugo static website generator on AWS Lambda](http://bezdelev.com/post/hugo-aws-lambda-static-website/) by Ilya Bezdelev.

1. Merging changes to master branch in Git will trigger a Git hook that notifies a Lambda function.
2. Lambda Function
    1. Clone Git repo
    2. Run `hugo`
    3. Copy generated files to static webhost S3 bucket

The configuration in Ilya's article is quite intimidating (lots of entering text into GUI boxes), so I think I will look into using [Serverless](https://serverless.com) to describe and deploy this architecture.

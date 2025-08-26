# Overview

## Creation/Consumption

As stated before, the core goal of `OpsML` is to provide quality control to AI artifact management. And while part of artifact management involves how artifacts are created (model training, data creation, experiments, etc.), the other part of artifact management is how artifacts are consumed as in APIs.

With this in mind, `OpsML` provides a variety of helpers that enable you to use your model(s)/service(s) in any API framework.

The following code examples utilize `FastAPI` to demonstrate how to create API endpoints for your models/services. In fact

<h1 align="center">
  <br>
  <img src="../../images/card_deployment.png"  width="700"alt="card deployment"/>
  <br>
</h1>


## Downloading a Model

Before loading an model into an api, we first need a model. The following code will create 2 models and bundle them into a `ServiceCard`.
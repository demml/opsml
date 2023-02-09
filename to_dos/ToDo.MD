# List of Tasks to Complete

## For open-source
- [ ] Make sure no credentials are being pulled during tests (remove them from the env)
- [ ] Make contributor contract doc
- [ ] Create PR template

## General
- [ ] Add additional SQL connection for cloudsql postgres, Bigquery and Snowflake
- [ ] Create interface for connecting to different reigstry DBs with different storage backends (i.e., what would it look like to instantiate the card registry with a Snowflake sql connection and GCS storage client?)
- [ ] Increase unit-test coverage
- [ ] Typing needs review
- [ ] Create UML for high-level design
- [ ] Refactor pipeline Viz code

## ModelCard tasks
- [ ] Fully test Tensorflow and Pytorch implementations for onnx conversion
- [ ] Auto-generate api sig for Seldon (When modelcard is called from registry/gcs it should come with the Onnx Proto and the API sig for Seldon). Ideally, it would be great if only model args are needed to spin up a Seldon api (standardized env)
- [ ] Create Onnx auto converters for simple pre and post-processing through extension libraries (https://github.com/microsoft/onnxruntime-extensions) - this may only apply to deep learning models. Artifacts already supports sklearn pipelines, which can include pre and post-processors



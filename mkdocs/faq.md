# Frequently asked questions

## How does it differ from MLflow?

There’s an overlap in features, but the scope is different:

* With MLtraq, tracking the state is so transparent that it feels like checkpointing the experiment for later analysis and continuation. With robust/flexible serialization, experiments can easily copy/load to new databases. In MLflow, tracking is designed to track metrics and only a little more. The setup is less flexible, but you have more readily available integrations.

* With MLflow, the emphasis is on covering the complete lifecycle, including model versioning and artifacts storage. MLtraq emphasizes experimentation, with an excellent model for experiments inspired by state monads from functional programming that encourages incapsulation/composition and parameter grids to simplify exploration.

In summary, MLflow is a better fit if you prioritize MLOps. MLtraq is a good candidate for experimentation.

## Does it work for Torch models, too?

Yes, MLtraq is agnostic to the specific model choice.
To add a PyTorch model, we can start with the [IRIS Flowers Classification example](./index.md#example-3-iris-flowers-classification). Using a [skorch classifier](https://skorch.readthedocs.io/en/stable/classifier.html), we can add one more scikit-learn compatible model. Alternatively, one can redesign the train_predict step without using scikit-learn. The results will include the accuracy score for the newly added model.

## Can it track the model's state during training, even if there's an early stop, for later continuation?

With MLtraq, You can dump and load arbitrary objects, including model weights and other state parameters. Let's consider the example on [artifacts storage](./howto/02-artifacts-storage.md). MLtraq dumps and reloads from the filesystem the binary blobs referenced in the tracked metadata. Similarly, you can store artifacts in third-party services and data stores.
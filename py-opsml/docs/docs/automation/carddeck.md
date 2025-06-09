# CardDeck

Just like you can create cards, you can also create a deck of cards called a `CardDeck`. The most important benefit of a `CardDeck` is that is allows you to create a collection of cards that can be loaded and used together. 

A prime example of this is in model apis where you may need to load more than one model, or an agentic workflows that associated with a more than one prompt. By using a `CardDeck`, you can group these cards together and load them all at once (with a few extra nice features that we'll get into).

### Create a CardDeck
```python
deck = CardDeck(
    space="opsml-space",
    name="opsml-deck",
    cards=[
        Card(
            alias="model1",
            uid=modelcard1.uid,
            registry_type=RegistryType.Model,
        ),
        Card(
            alias="model2",
            uid=modelcard2.uid,
            registry_type=RegistryType.Model,
        ),
    ],
)
registry.register_card(deck)
```

### Using a CardDeck in FastAPI
```python


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    logger.info("Starting up FastAPI app")

    fast_app.state.deck = deck = CardDeck.load_from_path( # (1)
        path=settings.card_deck_path
        ) 
    yield

    logger.info("Shutting down FastAPI app")
    
    # Shutdown the card deck
    fast_app.state.deck = None


app = FastAPI(lifespan=lifespan)

@app.post("/predict_with_model1", response_model=Response)
async def predict_model_1(request: Request, payload: PredictRequest) -> Response:
    card = cast(ModelCard, request.app.state.deck["model1"]) # (2)

    prediction= card.interface.model.predict(payload.to_numpy())

    return Response(prediction=prediction[0])

@app.post("/predict_with_model2", response_model=Response)
async def predict_model_2(request: Request, payload: PredictRequest) -> Response:
    card = cast(ModelCard, request.app.state.deck["model2"])

    prediction= card.interface.model.predict(payload.to_numpy())

    return Response(prediction=prediction[0])
```

1. Load the `CardDeck` and it's components directly from a path after downloading with the Opsml CLI
2. Access a specific card in the deck by its alias. This allows you to use the card's interface to perform operations, such as making predictions with a model.


Currently you can create a card deck through the client api or through a tool configuration in your `pyproject.toml` file.

## Create a Deck (API)

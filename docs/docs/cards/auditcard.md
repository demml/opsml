# Overview

`AuditCards` serve a special purpose in `OpsML` and can be viewed as a card that contains governance, compliance, and ethical information about a particular model and its associated assets. Importantly, information contained in an `AuditCard` can be used be governing bodies and stakeholders to assess and approve a model for production.

`AuditCards` are created by instantiating the `AuditCard` class and passing in the required arguments. When working in python, you can list and answer questions as part of your normal workflow. However, the easiest and most intuitive way to create and update `AuditCards` is through the `OpsML` UI (Audit tab). 

## Code Example

```python
from opsml.registry import AuditCard, CardRegistry

... # create model and data cards

auditcard = AuditCard(
    name="linear-regressor-audit",
    team="my_team", 
    user_email="user_email"
)

# add modelcard to auditcard
auditcard.add_card(modelcard)


# list questions
auditcard.list_questions()

# list by section
card.list_questions(section="business")

# answer question
card.answer_question(section="business", question_nbr=1, response="response")

# register
audit_registry = CardRegistry("audit")
audit_registry.register_card(auditcard)
```

# AuditCard Audit Sections

`business`
: question related to {{high level description here}}

`data_understanding`
: question related to {{high level description here}}

`data_preparation`
: question related to {{high level description here}}

`modeling`
: question related to {{high level description here}}

`evaluation`
: question related to {{high level description here}}

`deployment`
: question related to {{high level description here}}

`misc`
: question related to {{high level description here}}
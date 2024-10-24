# automaited Python API library
The automaited Python library provides convenient access to the automaited REST API from any Python 3.10+ application. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients powered by httpx.

## Installation

> [!IMPORTANT]
> The document extraction service is currently in a closed beta.

```sh
# install from PyPI
pip install automaited
```

## Usage

Define the target model you want to populate and pass it with the PDF that you want to process into the `.extract_model()` method. Here is an example:

```python
from datetime import date
from pydantic import Field, BaseModel
from automaited import DocExtClient
# from automaited import AsyncDocExtClient

class Article(BaseModel):
    article_number: str = Field(..., description="Typically alphabetical or alphanumerical.")
    description: str = Field(..., description="Description of the item.")
    quantity: float = Field(..., description="Number of pieces.")

class PurchaseOrder(BaseModel):
    customer_name: str = Field(..., description="Examples: Kaladent Inc., Henkel GmbH")
    order_number: str = Field(..., description="The purchase order number.")
    order_date: date = Field(..., description="The purchase order date.")
    items: list[Article] = Field(default_factory=list, description="List of all ordered articles.")

client = DocExtClient(API_KEY="TEST_BETA:you@company.com") # Replace the email with yours. As soon as we are out of beta you will receive a proper API key for production.
result: PurchaseOrder = client.extract_model(PurchaseOrder, "./po.pdf") # automaited.dev/samples
print(result)
```

You can download a sample PDF here: [automaited.dev/samples](https://www.automaited.dev/samples)
If you want to learn more about how to define target models, just take a look at the [pydantic docs](https://docs.pydantic.dev/latest/)

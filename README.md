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

Define the target model you want to populate and pass it with the PDF that you want to process into the `.extract_model()` method. 
Your first 1000 documents are free, just make sure to replace your email in the `API_KEY`. You will receive a verification mail with a link after running your extraction for the first time.
The first run will fail, becuase your email (defined in your api key) isn't verified yet. After verification you can re-run your script and it should work.
Here is an example:

```python
from datetime import date
from pydantic import Field, BaseModel
from automaited import DocExtClient
# from automaited import AsyncDocExtClient

class Article(BaseModel):
    article_number: str | None = Field(None, description="Typically alphabetical or alphanumerical.")
    description: str | None = Field(None, description="Description of the item.")
    quantity: float | None = Field(None, description="Number of pieces.")

class PurchaseOrder(BaseModel):
    customer_name: str | None = Field(None, description="Examples: Kaladent Inc., Henkel GmbH")
    order_number: str | None = Field(None, description="The purchase order number.")
    order_date: date | None = Field(None, description="The purchase order date.")
    items: list[Article] = Field(default_factory=list, description="List of all ordered articles.")

client = DocExtClient(API_KEY="TEST_BETA:you@company.com") # Replace the email with yours. As soon as we are out of beta you will receive a proper API key for production.
result: PurchaseOrder = client.extract_model(PurchaseOrder, "./po.pdf") # automaited.dev/samples
print(result)
```

You can download a sample PDF here: [automaited.dev/samples](https://www.automaited.dev/samples)
If you want to learn more about how to define target models, just take a look at the [pydantic docs](https://docs.pydantic.dev/latest/)

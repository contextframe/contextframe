---
url: "https://docs.litellm.ai/docs/budget_manager"
title: "Budget Manager | liteLLM"
---

[Skip to main content](https://docs.litellm.ai/docs/budget_manager#__docusaurus_skipToContent_fallback)

On this page

# Budget Manager

Don't want to get crazy bills because either while you're calling LLM APIs **or** while your users are calling them? use this.

info

If you want a server to manage user keys, budgets, etc. use our [LiteLLM Proxy Server](https://docs.litellm.ai/docs/proxy/virtual_keys)

LiteLLM exposes:

- `litellm.max_budget`: a global variable you can use to set the max budget (in USD) across all your litellm calls. If this budget is exceeded, it will raise a BudgetExceededError
- `BudgetManager`: A class to help set budgets per user. BudgetManager creates a dictionary to manage the user budgets, where the key is user and the object is their current cost + model-specific costs.
- `LiteLLM Proxy Server`: A server to call 100+ LLMs with an openai-compatible endpoint. Manages user budgets, spend tracking, load balancing etc.

## quick start [​](https://docs.litellm.ai/docs/budget_manager\#quick-start "Direct link to quick start")

```codeBlockLines_e6Vv
import litellm, os
from litellm import completion

# set env variable
os.environ["OPENAI_API_KEY"] = "your-api-key"

litellm.max_budget = 0.001 # sets a max budget of $0.001

messages = [{"role": "user", "content": "Hey, how's it going"}]
completion(model="gpt-4", messages=messages)
print(litellm._current_cost)
completion(model="gpt-4", messages=messages)

```

## User-based rate limiting [​](https://docs.litellm.ai/docs/budget_manager\#user-based-rate-limiting "Direct link to User-based rate limiting")

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BerriAI/litellm/blob/main/cookbook/LiteLLM_User_Based_Rate_Limits.ipynb)

```codeBlockLines_e6Vv
from litellm import BudgetManager, completion

budget_manager = BudgetManager(project_name="test_project")

user = "1234"

# create a budget if new user user
if not budget_manager.is_valid_user(user):
    budget_manager.create_budget(total_budget=10, user=user)

# check if a given call can be made
if budget_manager.get_current_cost(user=user) <= budget_manager.get_total_budget(user):
    response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hey, how's it going?"}])
    budget_manager.update_cost(completion_obj=response, user=user)
else:
    response = "Sorry - no budget!"

```

[**Implementation Code**](https://github.com/BerriAI/litellm/blob/main/litellm/budget_manager.py)

## use with Text Input / Output [​](https://docs.litellm.ai/docs/budget_manager\#use-with-text-input--output "Direct link to use with Text Input / Output")

Update cost by just passing in the text input / output and model name.

```codeBlockLines_e6Vv
from litellm import BudgetManager

budget_manager = BudgetManager(project_name="test_project")
user = "12345"
budget_manager.create_budget(total_budget=10, user=user, duration="daily")

input_text = "hello world"
output_text = "it's a sunny day in san francisco"
model = "gpt-3.5-turbo"

budget_manager.update_cost(user=user, model=model, input_text=input_text, output_text=output_text) # 👈
print(budget_manager.get_current_cost(user))

```

## advanced usage [​](https://docs.litellm.ai/docs/budget_manager\#advanced-usage "Direct link to advanced usage")

In production, we will need to

- store user budgets in a database
- reset user budgets based on a set duration

### LiteLLM API [​](https://docs.litellm.ai/docs/budget_manager\#litellm-api "Direct link to LiteLLM API")

The LiteLLM API provides both. It stores the user object in a hosted db, and runs a cron job daily to reset user-budgets based on the set duration (e.g. reset budget daily/weekly/monthly/etc.).

**Usage**

```codeBlockLines_e6Vv
budget_manager = BudgetManager(project_name="<my-unique-project>", client_type="hosted")

```

**Complete Code**

```codeBlockLines_e6Vv
from litellm import BudgetManager, completion

budget_manager = BudgetManager(project_name="<my-unique-project>", client_type="hosted")

user = "1234"

# create a budget if new user user
if not budget_manager.is_valid_user(user):
    budget_manager.create_budget(total_budget=10, user=user, duration="monthly") # 👈 duration = 'daily'/'weekly'/'monthly'/'yearly'

# check if a given call can be made
if budget_manager.get_current_cost(user=user) <= budget_manager.get_total_budget(user):
    response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hey, how's it going?"}])
    budget_manager.update_cost(completion_obj=response, user=user)
else:
    response = "Sorry - no budget!"

```

### Self-hosted [​](https://docs.litellm.ai/docs/budget_manager\#self-hosted "Direct link to Self-hosted")

To use your own db, set the BudgetManager client type to `hosted` **and** set the api\_base.

Your api is expected to expose `/get_budget` and `/set_budget` endpoints. [See code for details](https://github.com/BerriAI/litellm/blob/27f1051792176a7eb1fe3b72b72bccd6378d24e9/litellm/budget_manager.py#L7)

**Usage**

```codeBlockLines_e6Vv
budget_manager = BudgetManager(project_name="<my-unique-project>", client_type="hosted", api_base="your_custom_api")

```

**Complete Code**

```codeBlockLines_e6Vv
from litellm import BudgetManager, completion

budget_manager = BudgetManager(project_name="<my-unique-project>", client_type="hosted", api_base="your_custom_api")

user = "1234"

# create a budget if new user user
if not budget_manager.is_valid_user(user):
    budget_manager.create_budget(total_budget=10, user=user, duration="monthly") # 👈 duration = 'daily'/'weekly'/'monthly'/'yearly'

# check if a given call can be made
if budget_manager.get_current_cost(user=user) <= budget_manager.get_total_budget(user):
    response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hey, how's it going?"}])
    budget_manager.update_cost(completion_obj=response, user=user)
else:
    response = "Sorry - no budget!"

```

## Budget Manager Class [​](https://docs.litellm.ai/docs/budget_manager\#budget-manager-class "Direct link to Budget Manager Class")

The `BudgetManager` class is used to manage budgets for different users. It provides various functions to create, update, and retrieve budget information.

Below is a list of public functions exposed by the Budget Manager class and their input/outputs.

### **init** [​](https://docs.litellm.ai/docs/budget_manager\#init "Direct link to init")

```codeBlockLines_e6Vv
def __init__(self, project_name: str, client_type: str = "local", api_base: Optional[str] = None)

```

- `project_name` (str): The name of the project.
- `client_type` (str): The client type ("local" or "hosted"). Defaults to "local".
- `api_base` (Optional\[str\]): The base URL of the API. Defaults to None.

### create\_budget [​](https://docs.litellm.ai/docs/budget_manager\#create_budget "Direct link to create_budget")

```codeBlockLines_e6Vv
def create_budget(self, total_budget: float, user: str, duration: Literal["daily", "weekly", "monthly", "yearly"], created_at: float = time.time())

```

Creates a budget for a user.

- `total_budget` (float): The total budget of the user.
- `user` (str): The user id.
- `duration` (Literal\["daily", "weekly", "monthly", "yearly"\]): The budget duration.
- `created_at` (float): The creation time. Default is the current time.

### projected\_cost [​](https://docs.litellm.ai/docs/budget_manager\#projected_cost "Direct link to projected_cost")

```codeBlockLines_e6Vv
def projected_cost(self, model: str, messages: list, user: str)

```

Computes the projected cost for a session.

- `model` (str): The name of the model.
- `messages` (list): The list of messages.
- `user` (str): The user id.

### get\_total\_budget [​](https://docs.litellm.ai/docs/budget_manager\#get_total_budget "Direct link to get_total_budget")

```codeBlockLines_e6Vv
def get_total_budget(self, user: str)

```

Returns the total budget of a user.

- `user` (str): user id.

### update\_cost [​](https://docs.litellm.ai/docs/budget_manager\#update_cost "Direct link to update_cost")

```codeBlockLines_e6Vv
def update_cost(self, completion_obj: ModelResponse, user: str)

```

Updates the user's cost.

- `completion_obj` (ModelResponse): The completion object received from the model.
- `user` (str): The user id.

### get\_current\_cost [​](https://docs.litellm.ai/docs/budget_manager\#get_current_cost "Direct link to get_current_cost")

```codeBlockLines_e6Vv
def get_current_cost(self, user: str)

```

Returns the current cost of a user.

- `user` (str): The user id.

### get\_model\_cost [​](https://docs.litellm.ai/docs/budget_manager\#get_model_cost "Direct link to get_model_cost")

```codeBlockLines_e6Vv
def get_model_cost(self, user: str)

```

Returns the model cost of a user.

- `user` (str): The user id.

### is\_valid\_user [​](https://docs.litellm.ai/docs/budget_manager\#is_valid_user "Direct link to is_valid_user")

```codeBlockLines_e6Vv
def is_valid_user(self, user: str) -> bool

```

Checks if a user is valid.

- `user` (str): The user id.

### get\_users [​](https://docs.litellm.ai/docs/budget_manager\#get_users "Direct link to get_users")

```codeBlockLines_e6Vv
def get_users(self)

```

Returns a list of all users.

### reset\_cost [​](https://docs.litellm.ai/docs/budget_manager\#reset_cost "Direct link to reset_cost")

```codeBlockLines_e6Vv
def reset_cost(self, user: str)

```

Resets the cost of a user.

- `user` (str): The user id.

### reset\_on\_duration [​](https://docs.litellm.ai/docs/budget_manager\#reset_on_duration "Direct link to reset_on_duration")

```codeBlockLines_e6Vv
def reset_on_duration(self, user: str)

```

Resets the cost of a user based on the duration.

- `user` (str): The user id.

### update\_budget\_all\_users [​](https://docs.litellm.ai/docs/budget_manager\#update_budget_all_users "Direct link to update_budget_all_users")

```codeBlockLines_e6Vv
def update_budget_all_users(self)

```

Updates the budget for all users.

### save\_data [​](https://docs.litellm.ai/docs/budget_manager\#save_data "Direct link to save_data")

```codeBlockLines_e6Vv
def save_data(self)

```

Stores the user dictionary.

- [quick start](https://docs.litellm.ai/docs/budget_manager#quick-start)
- [User-based rate limiting](https://docs.litellm.ai/docs/budget_manager#user-based-rate-limiting)
- [use with Text Input / Output](https://docs.litellm.ai/docs/budget_manager#use-with-text-input--output)
- [advanced usage](https://docs.litellm.ai/docs/budget_manager#advanced-usage)
  - [LiteLLM API](https://docs.litellm.ai/docs/budget_manager#litellm-api)
  - [Self-hosted](https://docs.litellm.ai/docs/budget_manager#self-hosted)
- [Budget Manager Class](https://docs.litellm.ai/docs/budget_manager#budget-manager-class)
  - [**init**](https://docs.litellm.ai/docs/budget_manager#init)
  - [create\_budget](https://docs.litellm.ai/docs/budget_manager#create_budget)
  - [projected\_cost](https://docs.litellm.ai/docs/budget_manager#projected_cost)
  - [get\_total\_budget](https://docs.litellm.ai/docs/budget_manager#get_total_budget)
  - [update\_cost](https://docs.litellm.ai/docs/budget_manager#update_cost)
  - [get\_current\_cost](https://docs.litellm.ai/docs/budget_manager#get_current_cost)
  - [get\_model\_cost](https://docs.litellm.ai/docs/budget_manager#get_model_cost)
  - [is\_valid\_user](https://docs.litellm.ai/docs/budget_manager#is_valid_user)
  - [get\_users](https://docs.litellm.ai/docs/budget_manager#get_users)
  - [reset\_cost](https://docs.litellm.ai/docs/budget_manager#reset_cost)
  - [reset\_on\_duration](https://docs.litellm.ai/docs/budget_manager#reset_on_duration)
  - [update\_budget\_all\_users](https://docs.litellm.ai/docs/budget_manager#update_budget_all_users)
  - [save\_data](https://docs.litellm.ai/docs/budget_manager#save_data)
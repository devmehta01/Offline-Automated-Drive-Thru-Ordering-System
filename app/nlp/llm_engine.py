from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import json

class LlmEngine:
    def __init__(self, model_name="mistral"):
        self.llm = OllamaLLM(model=model_name)

        self.prompt = PromptTemplate.from_template('''
You are an order processing assistant for a restaurant.

Here is the current order so far (in JSON format):
{current_order}

The customer now said:
{order_text}

Instructions:
- DO NOT remove or forget any existing items unless the customer explicitly says to cancel.
- ALWAYS copy all existing items exactly as they are unless being modified.
- Only use \"action\": "add", "modify", or "remove". No other action types allowed.
- If any other action like \"copy\", \"nochange\", \"none\" is created, it is INVALID. Only use \"add\", \"modify\", \"remove\".
- If the customer says \"another\", \"one more\", or similar, increment the quantity of the existing item by 1.
- Special instructions (like \"no onions\") must be added to the \"instructions\" list.
- Each item must have: item name, quantity, instructions (list), and action.
- If modifying, preserve existing instructions unless the user asks to change them.
- Add new items if requested.
- When the customer says \"remove one\", decrease the quantity of the matching item by 1.
- If the quantity reaches zero after removal, REMOVE the item entirely from the order. It must NOT appear with quantity 0.
- If nothing changed in the order, simply repeat the existing order exactly without inventing new actions or items.
- Do not invent or modify quantities unless explicitly told.
- Never blindly copy example data. Always reason based on the current conversation.

STRICTLY return only valid JSON. No extra text, no explanations.

Respond in this format:

{{
  "order": [
    {{
      "item": "item name",
      "quantity": 1,
      "instructions": ["special instructions"],
      "action": "add" / "modify" / "remove"
    }}
  ]
}}
''')

    def parse_order(self, order_text, current_order="No previous order"):
        chain = self.prompt | self.llm
        response = chain.invoke({
            "order_text": order_text,
            "current_order": current_order
        })
        return response

# Example interactive testing
if __name__ == "__main__":
    engine = LlmEngine()
    current_order_json = "No previous order"

    while True:
        customer_input = input("\nCustomer says: ")

        if customer_input.lower() in ["done", "that is all", "confirm", "exit"]:
            print("\nFinal Order:\n", current_order_json)
            break

        response = engine.parse_order(customer_input, current_order=current_order_json)
        print("\n[LLM Response]")
        print(response)

        # Try updating current order
        try:
            parsed = json.loads(response)
            current_order_json = json.dumps(parsed, indent=2)
        except Exception as e:
            print("⚠️ Error parsing LLM response:", e)
            print("Response was:", response)

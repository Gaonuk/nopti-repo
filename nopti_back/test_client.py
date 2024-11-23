from openai import OpenAI
import instructor
from pydantic import BaseModel

# Configure the OpenAI client to use the custom API base
client = OpenAI(
    base_url="http://127.0.0.1:8111/v1",  # Assuming LLM Studio uses the /v1 endpoint
    api_key="not-needed",  # LLM studio often doesn't need a key. You can use any placeholder string if needed.
)

client_openai = instructor.from_openai(client)

def query_llm_studio(symstem_prompt,prompt, model_name="default"):  # Use "default" or your model name
    """
    Queries the LLM Studio model.

    Args:
        prompt (str): The text prompt to send to the model.
        model_name (str): The name of the model (default is usually "default").

    Returns:
        str: The model's response, or None if an error occurs.
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": symstem_prompt}
                ,{"role": "user", "content": prompt}]
        )
        # Assuming the response structure is the same as the OpenAI API
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying LLM Studio: {e}")
        return None
    

def query_llm_studio2(symstem_prompt,prompt, pydantic_model,model_name="default"):  # Use "default" or your model name
    """
    Queries the LLM Studio model.

    Args:
        prompt (str): The text prompt to send to the model.
        model_name (str): The name of the model (default is usually "default").

    Returns:
        str: The model's response, or None if an error occurs.
    """
    try:
            messages=[
                {"role": "system", "content": symstem_prompt}
                ,{"role": "user", "content": prompt}]


            completion, raw = client_openai.chat.create_with_completion(
            model=model_name,
            messages=messages,
            response_model=pydantic_model,
            # generation_config={
            #     "temperature": 0.0,
            #     "top_p": 1,
            #     "candidate_count": 1,
            #     "max_output_tokens": 8000,
            # },
            max_retries=10,
        )
            result = completion.model_dump()
            # Assuming the response structure is the same as the OpenAI API
            return result
    except Exception as e:
        print(f"Error querying LLM Studio: {e}")
        return None
# Example usage:
# symstem_prompt = "You are a helpful and harmless AI assistant."
# user_prompt = "What is 2+2 ?"
# model_response = query_llm_studio(symstem_prompt,user_prompt)

# if model_response:
#     print(f"Model response: {model_response}")
# else:
#     print("No response from the model.")


class UserInfo(BaseModel):
    name: str
    age: int

# Example usage:
symstem_prompt = "You are a helpful and harmless AI assistant."
user_prompt = "John Doe is 30 years old."

model_response = query_llm_studio2(symstem_prompt,user_prompt,UserInfo)

if model_response:
    print(f"Model response: {model_response}")
else:
    print("No response from the model.")
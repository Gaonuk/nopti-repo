from openai import OpenAI
from pydantic import BaseModel
import instructor
import json
import sys
import os

# Get the absolute path to the repository root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from models.ai_response import SimilarIDS


# Configure the OpenAI client to use the custom API base
client = OpenAI(
    base_url="http://127.0.0.1:8111/v1",  # Assuming LLM Studio uses the /v1 endpoint
    api_key="not-needed",  # LLM studio often doesn't need a key. You can use any placeholder string if needed.
)

client_openai = instructor.from_openai(client)



def query_llm_studio(symstem_prompt,prompt, pydantic_model,model_name="default"):  # Use "default" or your model name
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

            completion = client_openai.chat.create(
            model=model_name,
            messages=messages,
            response_model=pydantic_model,
            max_retries=10,
        )
            result = completion.model_dump_json()
            # Assuming the response structure is the same as the OpenAI API
            return result
    except Exception as e:
        print(f"Error querying LLM Studio: {e}")
        return None

# def get_list_10_similar( element : str):

#       # Load the JSON data from the file
#     with open('update_data_base/current_news_data.json', 'r') as file:
#          current_db = json.load(file)
#          print(current_db)
#     #read user_prompt

#     with open('prompts/user_prompt_get_10_similar_id.txt','r') as f:
#          user_template = f.read()
    
#     with open('prompts/system_prompt_get_10_similar_id.txt','r') as f:
#          user_template = f.read()
    
    
    
#     element_to_json = element

#     user_template = f"""
#         Here is the Key element : 
# {element}

# Here is the list of elements : 
# {current_db}
#         """
#     print(user_template)

#     response = query_llm_studio(symstem_prompt=user_template,prompt=user_template, pydantic_model=SimilarIDS,model_name="default")
#     return response


def get_list_10_similar( element : str):

      # Load the JSON data from the file
    with open('update_data_base/current_news_data.json', 'r') as file:
         current_db = json.load(file)
    
    return current_db['news_list'][:10]